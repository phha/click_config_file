#!/usr/bin/env python3

from functools import partial
from os import path
import click
import yaml


def configuation_option(*param_decls, **attrs):
    def decorator(f):
        def callback(saved_callback, ctx, param, value):
            if value is not None and path.isfile(value):
                with open(value) as f:
                    if not ctx.default_map:
                        ctx.default_map = {}
                    config_data = yaml.load(f)
                    for k, v in config_data.items():
                        ctx.default_map[k] = str(v)
            if saved_callback:
                return saved_callback(ctx, param, value)

        attrs.setdefault('is_eager', True)
        app_name, default_file = attrs.pop('config_file', None)
        if default_file:
            attrs['default'] = path.join(
                    click.get_app_dir(app_name), default_file)
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
        attrs['callback'] = partial(callback, attrs.get('callback', None))
        return click.option(*(param_decls or ('--config',)), **attrs)(f)
    return decorator
