import os
import pytest
import io
from contextlib import redirect_stdout, redirect_stderr
import subprocess

GMT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')

from lib.db import DB
from lib.global_config import GlobalConfig
from tests import test_functions as Tests
from lib.scenario_runner import ScenarioRunner

#pylint: disable=unused-argument # unused arguement off for now - because there are no running tests in this file
@pytest.fixture(name="reset_config")
def reset_config_fixture():
    config = GlobalConfig().config
    idle_start_time = config['measurement']['idle-time-start']
    idle_time_end = config['measurement']['idle-time-end']
    flow_process_runtime = config['measurement']['flow-process-runtime']
    yield
    config['measurement']['idle-time-start'] = idle_start_time
    config['measurement']['idle-time-end'] = idle_time_end
    config['measurement']['flow-process-runtime'] = flow_process_runtime

def test_global_timeout():

    measurement_total_duration = 1

    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/usage_scenarios/basic_stress.yml', skip_system_checks=True, dev_cache_build=False, dev_no_sleeps=True, dev_no_metrics=True, dev_no_phase_stats=True, measurement_total_duration=1)

    out = io.StringIO()
    err = io.StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            runner.run()
    except subprocess.TimeoutExpired as e:
        assert str(e).startswith("Command '['docker', 'run', '--rm', '-v',") and f"timed out after {measurement_total_duration} seconds" in str(e), \
        Tests.assertion_info(f"Command '['docker', 'run', '--rm', '-v', ... timed out after {measurement_total_duration} seconds", str(e))
        return
    except TimeoutError as e:
        assert str(e) == f"Timeout of {measurement_total_duration} s was exceeded. This can be configured in the user authentication for 'total_duration'.", \
        Tests.assertion_info(f"Timeout of {measurement_total_duration} s was exceeded. This can be configured in the user authentication for 'total_duration'.", str(e))
        return

    assert False, \
        Tests.assertion_info('Timeout was not raised', str(out.getvalue()))


def test_provider_disabling_not_active_by_default():


    out = io.StringIO()
    err = io.StringIO()

    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/stress-application/usage_scenario.yml', skip_unsafe=False, skip_system_checks=True, dev_cache_build=True, dev_no_sleeps=True, dev_no_metrics=False, dev_no_phase_stats=True)

    with redirect_stdout(out), redirect_stderr(err):
        with Tests.RunUntilManager(runner) as context:
            context.run_until('import_metric_providers')

    assert 'Not importing' not in out.getvalue()

def test_provider_disabling_working():
    GlobalConfig().override_config(config_location=f"{os.path.dirname(os.path.realpath(__file__))}/test-config-extra-network-and-duplicate-psu-providers.yml")

    out = io.StringIO()
    err = io.StringIO()

    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/stress-application/usage_scenario.yml', skip_unsafe=False, skip_system_checks=True, dev_cache_build=True, dev_no_sleeps=True, dev_no_metrics=False, dev_no_phase_stats=True, disabled_metric_providers=['NetworkConnectionsProxyContainerProvider'])

    with redirect_stdout(out), redirect_stderr(err):
        with Tests.RunUntilManager(runner) as context:
            context.run_until('import_metric_providers')

    assert 'Not importing NetworkConnectionsProxyContainerProvider as disabled per user settings' in out.getvalue()


def test_phase_padding_inactive():
    out = io.StringIO()
    err = io.StringIO()

    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/usage_scenarios/noop.yml', skip_system_checks=True, dev_no_metrics=True, dev_no_phase_stats=True, dev_no_sleeps=True, dev_cache_build=True, phase_padding=False)

    with redirect_stdout(out), redirect_stderr(err):
        run_id = runner.run()

    assert '>>>> MEASUREMENT SUCCESSFULLY COMPLETED <<<<' in out.getvalue()
    query = """
            SELECT
                time, note
            FROM
                notes
            WHERE
                run_id = %s
            ORDER BY
                time
            """

    notes = DB().fetch_all(query, (run_id,))

    # we count the array from the end as depending on if the test is executed alone or in conjunction with other tests 'alpine' will get pulled and produce a note at the beginning that extends the notes
    assert notes[-6][1] == 'Starting phase Testing Noop'
    assert notes[-5][1] == 'Ending phase Testing Noop [UNPADDED]'
    assert notes[-4][1] == 'Ending phase [RUNTIME] [UNPADDED]' # this implictely means we have no PADDED entries
    assert notes[-4][0] > notes[-3][0] - 300 # end times of reconstructed runtime and last sub-runtime are very close, but not exact, bc we only reconstruct phase_stats but not measurements table. 300 microseconds is a good cutoff

def test_phase_padding_active():
    out = io.StringIO()
    err = io.StringIO()

    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/usage_scenarios/noop.yml', skip_system_checks=True, dev_no_metrics=True, dev_no_phase_stats=True, dev_no_sleeps=True, dev_cache_build=True, phase_padding=True)

    with redirect_stdout(out), redirect_stderr(err):
        run_id = runner.run()

    assert '>>>> MEASUREMENT SUCCESSFULLY COMPLETED <<<<' in out.getvalue()
    query = """
            SELECT
                time, note
            FROM
                notes
            WHERE
                run_id = %s
            ORDER BY
                time
            """

    notes = DB().fetch_all(query, (run_id,))

    # we count the array from the end as depending on if the test is executed alone or in conjunction with other tests 'alpine' will get pulled and produce a note at the beginning that extends the notes
    assert notes[-9][1] == 'Starting phase Testing Noop'
    assert notes[-8][1] == 'Ending phase Testing Noop [UNPADDED]'
    assert notes[-7][1] == 'Ending phase Testing Noop [PADDED]'
    FROM_MS_TO_US = 1000
    assert notes[-7][0] - notes[-8][0] == runner._phase_padding_ms*FROM_MS_TO_US

    assert notes[-6][1] == 'Ending phase [RUNTIME] [UNPADDED]'



# Rethink how to do this test entirely
def wip_test_idle_start_time(reset_config):
    GlobalConfig().config['measurement']['idle-time-start'] = 2
    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/usage_scenarios/basic_stress.yml', skip_system_checks=True, dev_no_metrics=True, dev_no_phase_stats=True, dev_no_sleeps=True, dev_cache_build=True)
    run_id = runner.run()
    query = """
            SELECT
                time, note
            FROM
                notes
            WHERE
                run_id = %s
            ORDER BY
                time
            """

    notes = DB().fetch_all(query, (run_id,))

    timestamp_preidle = [note for note in notes if "Booting" in note[1]][0][0]
    timestamp_start = [note for note in notes if note[1] == 'Start of measurement'][0][0]

    #assert that the difference between the two timestamps is roughly 2 seconds
    diff = (timestamp_start - timestamp_preidle)/1000000
    assert 1.9 <= diff <= 2.1, \
        Tests.assertion_info('2s apart', f"timestamp difference of notes: {diff}s")

# Rethink how to do this test entirely
def wip_test_idle_end_time(reset_config):
    GlobalConfig().config['measurement']['idle-time-end'] = 2
    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/usage_scenarios/basic_stress.yml', skip_system_checks=True, dev_no_metrics=True, dev_no_phase_stats=True, dev_no_sleeps=True, dev_cache_build=True)
    run_id = runner.run()
    query = """
            SELECT
                time, note
            FROM
                notes
            WHERE
                run_id = %s
            ORDER BY
                time
            """

    notes = DB().fetch_all(query, (run_id,))
    timestamp_postidle = [note for note in notes if note[1] == 'End of post-measurement idle'][0][0]
    timestamp_end = [note for note in notes if note[1] == 'End of measurement'][0][0]

    #assert that the difference between the two timestamps is roughly 2 seconds
    diff = (timestamp_postidle - timestamp_end)/1000000
    assert 1.9 <= diff <= 2.1, \
        Tests.assertion_info('2s apart', f"timestamp difference of notes: {diff}s")

def wip_test_process_runtime_exceeded(reset_config):
    GlobalConfig().config['measurement']['flow-process-runtime'] = .1
    runner = ScenarioRunner(uri=GMT_DIR, uri_type='folder', filename='tests/data/usage_scenarios/basic_stress.yml', skip_system_checks=True, dev_no_metrics=True, dev_no_phase_stats=True, dev_no_sleeps=True, dev_cache_build=True)
    with pytest.raises(RuntimeError) as err:
        runner.run()
    expected_exception = 'Process exceeded runtime of 0.1s: stress-ng -c 1 -t 1 -q'
    assert expected_exception in str(err.value), \
        Tests.assertion_info(expected_exception, str(err.value))
