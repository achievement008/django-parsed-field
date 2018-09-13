import datetime
import json
import re

import requests
from simplejson import JSONDecodeError

REDUCERS = {
    'time': 'time mask',
    'regex': 'regular expression',
    'div': 'int value for div'
}


def prRed(prt): print("\033[91m{}\033[00m".format(prt))


def prGreen(prt): print("\033[92m{}\033[00m".format(prt))


def prYellow(prt): print("\033[93m{}\033[00m".format(prt))


def prLightPurple(prt): print("\033[94m{}\033[00m".format(prt))


def prPurple(prt): print("\033[95m{}\033[00m".format(prt))


def prCyan(prt): print("\033[96m{}\033[00m".format(prt))


def prLightGray(prt): print("\033[97m{}\033[00m".format(prt))


def prBlack(prt): print("\033[98m{}\033[00m".format(prt))


class RulesDictCreator:

    def __init__(self):
        self.rules = {}
        self.api_uri = None
        self.initial_data = None
        self.available_methods = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('f_')]

    def start(self):
        self.ask_for_uri()
        self.create_rules()

    def create_rules(self):
        print('Choose one of [{}] method or type "end parse" for end '.format(
            ', '.join([i[2:] for i in self.available_methods])), end='', flush=True)
        chosen_method = input()
        if not chosen_method or chosen_method == 'end parse':
            return self.rules
        else:
            try:
                method = getattr(self, 'f_' + chosen_method)
                method()
            except AttributeError:
                print('There is no "{}" method, try again'.format(chosen_method))
                self.create_rules()

    @staticmethod
    def get_relative(path, data):
        loop_arr = data
        if not path:
            return data
        for i in path.split('__'):
            try:
                loop_arr = loop_arr.get(i)
            except AttributeError:
                print('Error get "{}" value, check path '.format(i))
                return None
        return loop_arr

    def f_loop(self, data=None):
        data = data or self.initial_data
        print('Type path to list or dict ', end='', flush=True)
        path = input()
        loop_arr = self.get_relative(path, data)
        if not loop_arr:
            self.f_loop()
        else:
            if not isinstance(loop_arr, list) and not isinstance(loop_arr, dict):
                print('You can iterate just over list and dict objects: {} get, try again '.format(type(loop_arr)))
                self.f_loop()
            else:
                print('That\'s we get:')
                if isinstance(loop_arr, list):
                    item = loop_arr[0]
                else:
                    item = loop_arr.popitem()
                print(json.dumps(item, indent=2))

                print('Name for save in result json? [{}] '.format(path.split('__')[-1]), end='', flush=True)
                r_output_name = input()
                loop_rules = {'r_input_name': path, 'r_output_name': r_output_name or path.split('__')[-1],
                              'r_get': []}
                if isinstance(loop_arr, dict):
                    print('Type name for save dict key in result json or "pass": ', end='', flush=True)
                    r_dict_name_save = input()
                    if r_dict_name_save != 'pass':
                        prPurple('Reducers:')
                        reducers = self.get_reducers(item[0])
                        loop_rules['r_get'].append(
                            {'in': 'r_self', 'out': r_dict_name_save, 'r_reducers': reducers or {}})
                    item = item[1]
                keys_iterator = iter(item.keys())
                for key_item in keys_iterator:
                    print('Want to save "{}" value? Type name for result json or "pass" '.format(key_item), end='',
                          flush=True)
                    r_get_output_name = input()
                    if not r_get_output_name or r_get_output_name == 'pass':
                        continue
                    else:
                        prPurple('Reducers:')
                        reducers = self.get_reducers(item[key_item])
                        loop_rules['r_get'].append(
                            {'in': key_item, 'out': r_get_output_name, 'r_reducers': reducers or {}})

                self.add_loop_object(loop_rules)

    def f_get(self):
        print('Type relative path for search value ', end='', flush=True)
        path = input()
        r_get = self.get_relative(path, self.initial_data)
        if not r_get:
            print('Cant find {}, try again ', end='', flush=True)
        else:
            print('Type name for result json: ', end='', flush=True)
            r_get_output_name = input()
            r_get_arr = {'in': path, 'out': r_get_output_name or path.split('__')[-1]}
            self.add_get_object(r_get_arr)

    def get_reducers(self, item, reducers=None):
        print('Choose one of [lower, upper, div, time, time_st, regex] or type "pass"', end=' ', flush=True)
        red = input()
        if red == 'pass':
            return reducers
        if red not in ['lower', 'upper', 'div', 'time', 'time_st', 'regex']:
            self.get_reducers(reducers)
        else:
            if red in ['lower', 'upper', 'time_st']:
                reducers = self.append_to_reducers(red, '', reducers)
                self.get_reducers(item, reducers)
            else:
                print('Type {} for reduce value {}'.format(REDUCERS[red], item))
                ans = input()
                if red == 'div':
                    try:
                        print('Was: {}, will: {}'.format(item, float(item) / float(ans)))
                        reducers = self.append_to_reducers(red, ans, reducers)
                    except Exception as e:
                        print('Error in reduce value: {}'.format(e))
                elif red == 'time':
                    try:
                        print('Was: {}, will: {}'.format(item, datetime.datetime.strptime(item, ans)))
                        reducers = self.append_to_reducers(red, ans, reducers)
                    except Exception as e:
                        print('Error in reduce value: {}'.format(e))

                elif red == 'regex':
                    try:
                        print('Was: {}, will: {}'.format(item, re.sub(ans, '', item)))
                        reducers = self.append_to_reducers(red, ans, reducers)
                    except Exception as e:
                        print('Error in reduce value: {}'.format(e))
                self.get_reducers(item, reducers)
        return reducers

    @staticmethod
    def append_to_reducers(rule_name, rule, reducers):
        if reducers is None:
            reducers = {}
        reducers[rule_name] = rule
        return reducers

    def add_loop_object(self, loop_rules):
        if 'r_forloop' not in self.rules:
            self.rules['r_forloop'] = []
        self.rules['r_forloop'].append(loop_rules)
        return self.create_rules()

    def add_get_object(self, get_rules):
        if 'r_get' not in self.rules:
            self.rules['r_get'] = []
        self.rules['r_get'].append(get_rules)
        return self.create_rules()

    def ask_for_uri(self):
        print('Add api url and i will check keys/values for you! ', end='', flush=True)
        uri = input()
        if not uri or uri.lower() == 'n':
            print('No no no, get uri')
            self.ask_for_uri()
        else:
            if not uri.startswith('http'):
                print('Incorrect uri, must start with http/https. Try again...')
                self.ask_for_uri()
            else:
                self.api_uri = uri
                self.set_initial_data()

    def get_keys_tree(self, arr, tree: list):
        if isinstance(arr, dict):
            for key, value in arr.items():
                if isinstance(value, dict):
                    tree.append({key: self.get_keys_tree(value, [])})
                elif isinstance(value, list):
                    tree.append({key: self.get_keys_tree(value[0], [])})
                else:
                    tree.append('{}: {}'.format(key, type(value).__name__))
            return tree

    def set_initial_data(self):
        initial_data = requests.get(self.api_uri)
        try:
            self.initial_data = initial_data.json()
            prCyan(json.dumps(self.get_keys_tree(self.initial_data, []), indent=2))
        except JSONDecodeError:
            print('It\'s no json at {}. '.format(self.api_uri), end='', flush=True)
            self.ask_for_uri()


if __name__ == '__main__':
    a = RulesDictCreator()
    a.start()
    print(a.rules)
