import json
import os

from fastapi.responses import JSONResponse

from libs.k8s import K8s
from libs.process import *

from helpers.commons import *
from helpers.handle_exceptions import *

k8sv1 = K8s()


class Schedule:

    @handle_exceptions_async_method
    async def get(self, json_response=True):
        output = await run_process_check_output(['velero', 'schedule', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if 'error' in output:
            return output

        schedules = json.loads(output['data'])

        add_id_to_list(schedules['items'])

        res = {'data': {'payload': schedules}}

        if json_response:
            return JSONResponse(content=res, status_code=201)
        else:
            return schedules

    @handle_exceptions_async_method
    async def describe(self, schedule_name):
        if not schedule_name:
            return {'error': {'title': 'Error',
                              'description': 'Schedule name is required'
                              }
                    }

        output = await run_process_check_output(['velero', 'schedule', 'describe', schedule_name, '--colorized=false',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if 'error' in output:
            return output

        return {'data': {'payload': output['data']}}

    @handle_exceptions_async_method
    async def pause(self, schedule_name):
        if not schedule_name:
            return {'error': {'title': 'Error',
                              'description': 'Schedule name is required'
                              }
                    }

        output = await run_process_check_call(['velero', 'schedule', 'pause', schedule_name,
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Pause schedule',
                              'description': f"Schedule {schedule_name} pause request done!",
                              'type': 'info'
                              }
                             ]
                }

    @handle_exceptions_async_method
    async def unpause(self, schedule_name):
        if not schedule_name:
            return {'error': {'title': 'Error',
                              'description': 'Schedule name is required'
                              }
                    }

        output = await run_process_check_call(['velero', 'schedule', 'unpause', schedule_name,
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Pause schedule',
                              'description': f"Schedule {schedule_name} start request done!",
                              'type': 'info'
                              }
                             ]
                }

    @handle_exceptions_async_method
    async def create(self, info):

        if not info['values']['name'] or info['values']['name'] == '':
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }
        cmd = ['velero', 'schedule', 'create', info['values']['name'],
               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]

        cmd += parse_create_parameters(info)

        output = await run_process_check_call(cmd)
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Create schedule',
                              'description': f"Schedule {info['values']['name']} created!",
                              'type': 'info'
                              }
                             ]
                }

    @handle_exceptions_async_method
    async def delete(self, schedule_name):
        if not schedule_name:
            return {'error': {'title': 'Error',
                              'description': 'Schedule name is required'
                              }
                    }

        output = await run_process_check_call(['velero', 'schedule', 'delete', schedule_name, '--confirm',
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Delete schedule',
                              'description': f"Schedule {schedule_name} deleted request done!",
                              'type': 'info'
                              }
                             ]
                }

    @handle_exceptions_async_method
    async def update(self, info):

        if not info['values']['name'] or info['values']['name'] == '':
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }

        output = await k8sv1.update_velero_schedule(info['values'])

        if 'error' in output:
            return output

        return {'messages': [{'title': 'Create schedule',
                              'description': f"Schedule {info['values']['name']} created!",
                              'type': 'info'}]
                }
