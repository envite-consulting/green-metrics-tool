import os
import subprocess
import plistlib
from datetime import timezone
import time
import xml
import pandas
import signal

from metric_providers.base import MetricProviderConfigurationError, BaseMetricProvider

class PowermetricsProvider(BaseMetricProvider):
    def __init__(self, sampling_rate, skip_check=False):
        # We get this value on init as we want to have to for check_system to work in the normal case
        self._pm_process_count = self.powermetrics_total_count()

        super().__init__(
            metric_name='powermetrics',
            metrics={'time': int, 'value': int},
            sampling_rate=sampling_rate,
            unit='uJ',
            current_dir=os.path.dirname(os.path.abspath(__file__)),
            metric_provider_executable='/usr/bin/powermetrics',
            sudo=True,
            skip_check=skip_check,
        )

        self._skip_check =  skip_check

    def check_system(self, check_command="default", check_error_message=None, check_parallel_provider=True):
        # no call to super().check_system() as we have different logic of finding the process
        if self._pm_process_count > 0:
            raise MetricProviderConfigurationError('Another instance of powermetrics is already running on the system!\n'
                                                   'Please close it before running the Green Metrics Tool.\n'
                                                   'You can also override this with --skip-system-checks\n')

    def powermetrics_total_count(self):
        cmd = ['pgrep', '-ix', 'powermetrics']
        result = subprocess.run(cmd,
                                encoding='UTF-8',
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False)
        if result.returncode in [0, 1]:
            return len(result.stdout.strip().split('\n')) if result.stdout else 0

        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

    def is_our_powermetrics_running(self):
        total_count = self.powermetrics_total_count()
        minus_startup = total_count -  self._pm_process_count
        return  minus_startup >= 1

    def stop_profiling(self):
        if self._ps is None:
            return

        # Sending SIGIO shall tell the process to flush. Although the process does not seem
        # to react we keep it in, as it is common practice and don't expect it to have negative effects
        os.kill(self._ps.pid, signal.SIGIO)

        try:
            # We try calling the parent method which should work see
            # https://github.com/green-coding-solutions/green-metrics-tool/pull/566#discussion_r1429891190
            # but we keep the try to make sure that if we ever change the sudo call it still works
            super().stop_profiling()
        except PermissionError:
            # We will land here in any case as stated before (root permissions missing). When we trigger *killall* now
            # the process will be terminated. We opted for this implementation as other processes on the system, like
            # for instance the power hog (https://github.com/green-coding-solutions/hog) should not be affected too much.
            # They restart the process anyway when it gets killed. However manual processes that the user might have
            # started will also be killed, so we issue a notice.
            # There is really no better way of doing this as of now. Keeping the process id for instance in a hash and
            # killing only that would also fail du to root permissions missing. If we add an /etc/sudoers entry with a
            # wildcard for a PID we open up a security hole. Happy to take suggestions on this one!
            subprocess.check_output('sudo /usr/bin/killall powermetrics', shell=True)
            print('Killed powermetrics process with killall!')
            if self._pm_process_count > 0:
                print('-----------------------------------------------------------------------------------------------------------------')
                print('This means we will have also killed any other already running powermetrics process. Please restart them if needed!')
                print('-----------------------------------------------------------------------------------------------------------------')

        # As killall returns right after sending the SIGKILL we need to wait and make sure that the process
        # had time to flush everything to disk
        count = 0
        while self.is_our_powermetrics_running():
            print(f"Waiting for powermetrics to shut down (try {count}/60). Please do not abort ...")
            time.sleep(1)
            count += 1
            if count >= 60:
                subprocess.check_output('sudo /usr/bin/killall -9 powermetrics', shell=True)
                raise RuntimeError('powermetrics had to be killed with kill -9. Values can not be trusted!')

        self._ps = None

    def _add_extra_switches(self, call_string):
        # We can't use --show-all here as this sometimes triggers output on stderr
        return f"{call_string} --show-process-io --show-process-gpu --show-process-netstats --show-process-energy --show-process-coalition -f plist -b 0"

    def _parse_metrics(self, df):
        return df # noop, as we have already set detail_name individually in _read_metrics

    def _add_auxiliary_fields(self, df):
        # do not call parent as we have already set detail_name individually in _read_metrics
        df['sampling_rate_configured'] = self._sampling_rate
        return df

    def _check_resolution_underflow(self, df):
        pass # noop, as values with powermetrics exhibit sparse data very often and are 0

    def _read_metrics(self):

        with open(self._filename, 'rb') as metrics_file:
            datas = metrics_file.read()

        # Sometimes the container stops so fast that there will be no data in the file as powermetrics takes some time
        # to start. In this case we can't really do anything
        if datas == b'':
            return pandas.DataFrame()


        datas = datas.split(b'\x00')

        # We allow the usage of `df` and `dfs` here as it makes the code a lot more readable and is convention
        # pylint: disable=invalid-name
        dfs = []
        cum_time = None

        for count, data in enumerate(datas, start=1):
            try:
                data = plistlib.loads(data)
            except xml.parsers.expat.ExpatError as e:
                print('There was an error parsing the powermetrics data!')
                print(f"Iteration count: {count}")
                print(f"Number of items in datas: {len(datas)}")
                print(data)
                raise e

            if cum_time is None:
                # Convert seconds to nano seconds
                cum_time = int(data['timestamp'].replace(tzinfo=timezone.utc).timestamp() * 1e9)

            cum_time = cum_time + data['elapsed_ns']

            # we want microjoule. Therefore / 10**6 to get milli-seconds and the values are already in mW => ms * mW = uJ
            power_to_uJ = data['elapsed_ns'] / 1_000_000
            cum_time_ms = int(cum_time / 1_000)

            # coalitions gives us a list so we need to find the named entry
            docker_task = None
            for i in data['coalitions']:
                if i['name'] == 'com.docker.docker':
                    docker_task = i
                    break

            if docker_task is not None:
                dfs.append([cum_time_ms,
                            docker_task['cputime_ns'],
                            'cpu_time_powermetrics_vm',
                            'docker_vm',
                            'ns'])
                dfs.append([cum_time_ms,
                            docker_task['diskio_bytesread'],
                            'disk_io_bytesread_powermetrics_vm',
                            'docker_vm',
                            'Bytes'])
                dfs.append([cum_time_ms,
                            docker_task['diskio_byteswritten'],
                           'disk_io_byteswritten_powermetrics_vm',
                           'docker_vm',
                           'Bytes'])
                dfs.append([cum_time_ms,
                            int(docker_task['energy_impact']),
                           'energy_impact_powermetrics_vm',
                           'docker_vm',
                           # We need to introduce a new unit here as the energy impact on Mac isn't well understood
                           # https://tinyurl.com/2p9c56pz
                           '*'])

            if 'cpu_power' in data['processor']:
                dfs.append([cum_time_ms,
                            int(float(data['processor']['cpu_power']) * power_to_uJ),
                           'cores_energy_powermetrics_component',
                           '[COMPONENT]',
                           'uJ'])

            if 'package_joules' in data['processor']:
                dfs.append([cum_time_ms,
                            int(float(data['processor']['package_joules']) * 1_000_000),
                           'cpu_energy_powermetrics_component',
                           '[COMPONENT]',
                           'uJ'])

            if 'gpu_power' in data['processor']:
                dfs.append([cum_time_ms,
                            int(float(data['processor']['gpu_power']) * power_to_uJ),
                            'gpu_energy_powermetrics_component',
                            '[COMPONENT]',
                            'uJ'])

            #if 'combined_power' in data['processor']:
            #    dfs.append([cum_time_ms,
            #                int(float(data['processor']['combined_power']) * power_to_uJ),
            #                'system_combined_power',
            #                '[COMPONENT]',
            #                'uJ'])

            if 'ane_power' in data['processor']:
                dfs.append([cum_time_ms,
                            int(float(data['processor']['ane_power']) * power_to_uJ),
                            'ane_energy_powermetrics_component',
                            '[COMPONENT]',
                            'uJ'])

        df = pandas.DataFrame.from_records(dfs, columns=['time', 'value', 'metric', 'detail_name', 'unit'])

        if df.empty:
            raise RuntimeError(f"Metrics provider {self._metric_name} metrics log file was empty.")

        return df


    def filter_lines(self, stderr, f_strings):
        filtered_lines = [line for line in stderr.split('\n') if all(allowed_str not in line for allowed_str in f_strings)]
        return '\n'.join(filtered_lines).strip()


    def get_stderr(self):
        stderr = super().get_stderr()

        if not stderr:
            return stderr

        # powermetrics sometimes generates output to stderr. This isn't really a problem for our measurements
        # This has been showing up and we don't really understand why. Google has no results and looking at the
        # strings of powermetrics doesn't show anything. There also seems to be no correlation with the interval.
        # A shame we can't look into the code and figure this one out. For now we just ignore it as we don't really
        # have any other chance to debug.
        f_strings = ['proc_pid', 'Second underflow occured']
        return self.filter_lines(stderr, f_strings)
