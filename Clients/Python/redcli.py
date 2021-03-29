#!/usr/bin/env python
"""
Python CLI program to interface with redclient.py

TODO:
    - Finish adding functions
    - More robust error handling
"""

import redclient
import click
import json
import pprint

def get_config_values(config_file, *args, **kwargs):
    with open(config_file, 'r') as f:
        config = json.load(f)
    returns = []
    for arg in args:
        if arg in config:
            returns.append(config[arg])
        else:
            raise Exception("Key %s not in configuration file %s" %(arg, config_file))

    return tuple(returns)

def write_config_value(config_file, key, value):
    with open(config_file, 'r') as f:
        config = json.load(f)

    config[key] = value

    with open(config_file, 'w') as f:
        json.dump(config, f, indent="    ")

class NotRequiredIf(click.Option):
    """
    Taken from StackOverflow user Stephen Rauch and slightly modified
    (https://stackoverflow.com/questions/44247099/click-command-line-interfaces-make-options-required-if-other-optional-option-is) 
    """
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is not required if %s is provided' %
            self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, self.not_required_if))
            else:
                self.required = False

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)

@click.command()
@click.option("-c", "--config")
@click.option("-s", "--server", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-e", "--experiment_id", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-t", "--tables", required=True, cls=NotRequiredIf, not_required_if='config')
def cmd_create_experiment(config, server, experiment_id, tables):
    
    if config:
        server, experiment_id, tables = get_config_values(config, "server", "experiment_id", "tables")
    else:
        tables = eval(tables)
        
    key = redclient.create_experiment(server, experiment_id, tables)

    if key:
        print("Experiment Key:", key)
        print("Do not lose this key, you will need it to access experiment data later.")
        if config:
            write_config_value(config, "key", key)
            print("Experiment Key has been written to config file %s" %(config))

@click.command()
@click.option("-c", "--config")
@click.option("-s", "--server", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-e", "--experiment_id", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-k", "--key", required=True, cls=NotRequiredIf, not_required_if='config')
def cmd_get_number_participants(config, server, experiment_id, key):

    if config:
        server, experiment_id, key = get_config_values(config, "server", "experiment_id", "key")

    n_participants = redclient.get_number_participants(server, experiment_id, key)

    if n_participants:
        print("%s has %i participants registered." %(experiment_id, n_participants))

@click.command()
@click.option("-c", "--config")
@click.option("-s", "--server", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-e", "--experiment_id", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-k", "--key", required=True, cls=NotRequiredIf, not_required_if='config')
def cmd_get_participants(config, server, experiment_id, key):

    if config:
        server, experiment_id, key = get_config_values(config, "server", "experiment_id", "key")

    participants = redclient.get_participants(server, experiment_id, key)

    if participants:
        print("%s has the following participants registered:" %(experiment_id))
        pprint.pprint(participants)

@click.command()
@click.option("-c", "--config")
@click.option("-s", "--server", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-e", "--experiment_id", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-k", "--key", required=True, cls=NotRequiredIf, not_required_if='config')
def cmd_get_tables(config, server, experiment_id, key):

    if config:
        server, experiment_id, key = get_config_values(config, "server", "experiment_id", "key")

    tables = redclient.get_tables(server, experiment_id, key)

    if tables:
        print("%s has the following tables:" %(experiment_id))
        pprint.pprint(tables)

@click.command()
@click.option("-c", "--config")
@click.option("-s", "--server", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-e", "--experiment_id", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-k", "--key", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-p", "--participant_id", required=True)
@click.option("-T", "--table")
@click.option("-f", "--format", "fmt", type=click.Choice(["JSON", "CSV"], case_sensitive=False))
@click.option("-o", "--out", required=True)
def cmd_get_data(config, server, experiment_id, key, participant_id, table, fmt, out):

    if config:
        server, experiment_id, key = get_config_values(config, "server", "experiment_id", "key")

    kwargs = {}
    if table:
        kwargs["table"] = table
    if fmt:
        kwargs["fmt"] = fmt
        
    data = redclient.get_data(server, experiment_id, participant_id, key, **kwargs)

    if not out.endswith(".json"):
        out = out + ".json"
        
    with open(out, 'w') as f:
        f.write(data)

    print("Wrote data from %s for participant %s to file %s." %(experiment_id, participant_id, out))

@click.command()
@click.option("-c", "--config")
@click.option("-s", "--server", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-e", "--experiment_id", required=True, cls=NotRequiredIf, not_required_if='config')
@click.option("-P", "--prefix")
def cmd_register_participant(config, server, experiment_id, prefix):

    if config:
        server, experiment_id = get_config_values(config, "server", "experiment_id")

    kwargs = {}
    if prefix:
        kwargs["prefix"] = prefix

    participant_id = redclient.register_participant(server, experiment_id, **kwargs)

    if participant_id:
        print("Participant %s is now registered with experiment %s." %(participant_id, experiment_id))

        
class REDCLI(click.MultiCommand):
    commands = {
        "create-experiment": cmd_create_experiment,
        "get-number-participants": cmd_get_number_participants,
        "get-participants": cmd_get_participants,
        "get-tables": cmd_get_tables,
        "get-data": cmd_get_data,
        "register-participant": cmd_register_participant,
    }
    
    def list_commands(self, ctx):
        l = list(REDCLI.commands.keys())
        l.sort()
        return l

    def get_command(self, ctx, name):
        return REDCLI.commands[name]
        

if __name__ == '__main__':
    cli = REDCLI(help="Pass the --help option after a command to get more information on how to use that command.")
    cli()
    
