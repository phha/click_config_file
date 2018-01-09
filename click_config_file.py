from functools import partial
from os import path
import click
import configobj


def parse_config_file(file_name):
    return configobj.ConfigObj(file_name, unrepr=True)


def configuration_option(*param_decls, **attrs):
    def decorator(f):
        def callback(saved_callback, app_name, config_file_name, ctx, param,
                     value):
            if not ctx.default_map:
                ctx.default_map = {}
            if not app_name:
                app_name = ctx.info_name
            default_value = path.join(
                click.get_app_dir(app_name), config_file_name)
            param.default = default_value
            if not value:
                value = default_value
            if path.isfile(value):
                config = parse_config_file(value)
                for k, v in config.items():
                    ctx.default_map[k] = v
            return saved_callback(ctx, param, value) if saved_callback else value

        attrs.setdefault('is_eager', True)
        attrs.setdefault('help', 'Read configuration from PATH.')
        attrs.setdefault('expose_value', False)
        app_name = attrs.pop('app_name', None)
        config_file_name = attrs.pop('config_file_name', 'config')
        path_default_params = {
            'exists': False,
            'file_okay': True,
            'dir_okay': False,
            'writable': False,
            'readable': True,
            'resolve_path': True
        }
        path_params = {}
        for k, v in path_default_params.items():
            path_params[k] = attrs.pop(k, v)
        attrs['type'] = click.Path(**path_params)
        attrs['callback'] = partial(callback, attrs.get('callback', None),
                                    app_name, config_file_name)
        return click.option(*(param_decls or ('--config', )), **attrs)(f)

    return decorator
