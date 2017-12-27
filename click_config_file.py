#!/usr/bin/env python3

from functools import partial
from os import path
import click

def parse_config_file(file_name):
    with click.open_file(file_name, 'r') as f:
        return eval("{{{}}}".format(f.read()))

def configuation_option(*param_decls, **attrs):
    def decorator(f):
        def callback(saved_callback, app_name, config_file_name, ctx, param, value):
            if not value:
                if not app_name:
                    app_name = ctx.info_name
                value = path.join(click.get_app_dir(app_name), config_file_name)
            if path.isfile(value):
                config = parse_config_file(value)
                if not ctx.default_map:
                    ctx.default_map = {}
                for k, v in config.items():
                    ctx.default_map[k] = v
            if saved_callback:
                return saved_callback(ctx, param, value)
            else:
                return value

        attrs.setdefault('is_eager', True)
        app_name = attrs.pop('app_name', None)
        config_file_name = attrs.pop('config_file_name', 'config')
        path_default_params = {'exists': False,
                               'file_okay': True,
                               'dir_okay': False,
                               'writable': False,
                               'readable': True,
                               'resolve_path': True}
        path_params = {}
        for k, v in path_default_params.items():
            path_params[k] = attrs.pop(k, v)
        attrs['type'] = click.Path(**path_params)
        attrs['callback'] = partial(
            callback,
            attrs.get('callback', None),
            app_name,
            config_file_name)
        return click.option(*(param_decls or ('--config',)), **attrs)(f)
    return decorator
