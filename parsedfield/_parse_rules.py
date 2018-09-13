import datetime
import re


class RulesParser(object):
    def __init__(self, dict_of_rules, user_dict, dict_of_reduction=None):
        self.dict_of_rules = dict_of_rules
        self.user_dict = user_dict
        self.dict_of_reduction = dict_of_reduction
        self.searched = {}
        self.current_forloop = ''
        self.current_reduction_dict = {}
        self.reduction_names_list = []

    @staticmethod
    def get_relative(path, data):
        loop_arr = data
        if not path:
            return data
        for i in path.split('__'):
            try:
                loop_arr = loop_arr.get(i)
            except AttributeError:
                print('Error get "{0}" value, check path '.format(i))
                return None
        return loop_arr

    @staticmethod
    def check(u_dict, f_key):
        if isinstance(f_key, list):
            for item in f_key:
                if item not in u_dict:
                    raise ValueError('You must specify {0} in {1}'.format(item, u_dict))
        elif f_key not in u_dict:
            raise ValueError('You must specify {0} in {1}'.format(f_key, u_dict))
        else:
            return True

    @staticmethod
    def check_type(u_dict, s_type):
        if not isinstance(u_dict, s_type):
            raise ValueError('Incorrect type. Must be a {0}, you provide {1}.'.format(s_type, type(u_dict)))

    def get_items(self, u_arr, list_rules, self_name=None):
        self.check_type(list_rules, list)
        part = {}
        for rule_item in list_rules:
            if rule_item['in'] != 'r_self':
                val = u_arr[rule_item['in']]
            else:
                val = self_name
            val = self.make_conversions(val, rule_item['r_reducers'])
            part[rule_item['out']] = val

        return part

    def get_item(self, key):
        return self.user_dict[key]

    def parse(self):
        self.check_type(self.dict_of_rules, dict)
        for key, value in self.dict_of_rules.items():
            if key == 'r_forloop':
                self.check_type(value, list)
                self.r_forloop_parser(value)
            elif key == 'r_get':
                self.check_type(value, list)
                self.r_get_parser(value)
        return self.searched

    def r_forloop_parser(self, r_list):
        for item in r_list:
            self.check_type(item, dict)
            self.r_forloop(item)

    def r_forloop(self, f_dict):
        self.check(f_dict, ['r_get', 'r_input_name', 'r_output_name'])
        if self.current_forloop != f_dict['r_output_name']:
            self.current_forloop = f_dict['r_output_name']
            if self.dict_of_reduction is not None:
                self.find_reduction_for_forloop()
        self.searched[self.current_forloop] = []
        find_in = self.get_relative(f_dict['r_input_name'], self.user_dict)
        if isinstance(find_in, dict):
            for f_key, f_value in find_in.items():
                self.searched[self.current_forloop].append(self.get_items(f_value, f_dict['r_get'], f_key))
        elif isinstance(find_in, list):
            for item in find_in:
                self.searched[self.current_forloop].append(self.get_items(item, f_dict['r_get']))

    def r_get_parser(self, f_get_list):
        for get_item in f_get_list:
            self.searched[get_item['out']] = self.get_item(get_item['in'])

    @staticmethod
    def make_conversions(elem, rule_list):
        for rule_name, rule in rule_list.items():
            if rule_name == 'lower':
                elem = elem.lower()
            elif rule_name == 'upper':
                elem = elem.upper()
            elif rule_name == 'regex':
                elem = re.sub(rule, '', elem)
            elif rule_name == 'div':
                elem = float(elem) / float(rule)
            elif rule_name == 'time_st':
                elem = datetime.datetime.fromtimestamp(elem)
            elif rule_name == 'time':
                elem = datetime.datetime.strptime(elem, rule)
        return elem

    def find_reduction_for_forloop(self):
        for item in self.dict_of_reduction['r_forloop']:
            if item['r_name'] == self.current_forloop:
                self.current_reduction_dict = item['r_reducers']
                return
            self.current_reduction_dict = None
