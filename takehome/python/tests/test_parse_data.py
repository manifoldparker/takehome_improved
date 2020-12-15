from unittest import TestCase
import json
import process_json


def run_parse_data_on_string(data:str):
    """
    Runs the process_json.parse_data on the supplied data string, searching specifically for a "first_name" field
    :param data: a JSON formatted string to be searched
    :return: the results of running parse_data for "first_name"
    """
    data_dict = json.loads(data)
    results = process_json.parse_data(data_dict)
    return results


class TestParseData(TestCase):

    def setUp(self):
        self.base_dict = \
            {
                "middle_name": "Rivera",
                "first_name": "Shirley",
                "last_name": "Anne",
                "zip_code": 12345
            }

    def test_parse_data_empty_dict(self):
        """
        Tests the case where we pass an empty dictionary. Expects the function to return nothing found but
        populate the dictionary with the record_id
        :return:
        """
        num_fields, parsed_res = process_json.parse_data( {})

        #expected result is empty
        self.assertEqual(0,num_fields)

        self.assertIn(process_json.record_id_key, parsed_res)

    def test_parse_data_bad_input_none(self):
        """
        Tests the case where we pass None
        :return:
        """
        num_fields,parsed_res = process_json.parse_data( None)

        # expected result is empty
        self.assertEqual(0,num_fields)
        self.assertIn(process_json.record_id_key, parsed_res)

    def test_parse_data_bad_input_list(self):
        """
        Tests the case where we pass a list
        :return:
        """
        num_fields,parsed_res = process_json.parse_data( ["Shirley", "Bob"])

        # expected result is empty
        self.assertEqual(0,num_fields)
        self.assertIn(process_json.record_id_key, parsed_res)

    def test_parse_data_bad_input_empty_string(self):
        """
        Tests the case where we pass None
        """
        num_fields,parsed_res = process_json.parse_data( "")

        # expected result is empty
        self.assertEqual(0,num_fields)
        self.assertIn(process_json.record_id_key, parsed_res)

    def test_parse_data(self):
        """
        Tests the most basic case of parse_data, where all fields are present
        """
        input_data = """
        {
            "middle_name": "Rivera",
            "first_name": "Shirley", 
            "last_name": "Anne", 
            "zip_code": 12345
        }
        """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(4, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key) #remove the record ID to compare against the expected dict

        self.assertEqual(self.base_dict,parsed_res)

    def test_parse_data_nested_dict(self):
        """
        Tests the case where the expected field is nested within a top level dictionary
        """
        input_data = """
        {
            "data":
            {
                "first_name": "Shirley",
                "middle_name": "Rivera",
                "last_name": "Anne",
                "zip_code": 12345
            }
        }
        """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(4, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key)  # remove the record ID to compare against the expected dict

        self.assertEqual(self.base_dict, parsed_res)

    def test_parse_data_multiple_entries(self):
        """
        Tests the case where we provide a JSON string that has multiple first_name entries in the same dict.
        The expectation is that the JSON parser itself should ovveride the second instance with the first, as
        dicts have unique keys
        """

        input_data = """
                {
                    "data":
                    {
                        "first_name": "Rivera",
                        "first_name": "Shirley",
                        "last_name": "Anne",
                        "zip_code": 12345
                    }
                }
                """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(3, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key)  # remove the record ID to compare against the expected dict

        self.base_dict["middle_name"]=""
        self.assertEqual(self.base_dict, parsed_res)

    def test_parse_data_list(self):
        """
        Tests the case where first_name is a list of items, and expecting the parse_data to pull the first one
        """
        input_data = """
                {
                    "first_name":
                    [
                        "Shirley",
                        "Rivera",
                        "Anne"
                    ]
                }
                """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(1, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key)  # remove the record ID to compare against the expected dict

        base_dict= \
            {
                "middle_name": "",
                "first_name": "Shirley",
                "last_name": "",
                "zip_code": ""
            }

        self.assertEqual(base_dict,parsed_res)

    def test_parse_data_complex_structure_1(self):
        """
        Tests a more complex structure, where the first_name is nested well into the second element, verifying
        recursion and >1 element structures
        :return:
        """
        input_data = """
                        {
                            "adata":
                            [
                                "one",
                                "two",
                                "three"
                            ],
                            "data":
                            {
                                "middle_name": "Rivera",
                                "last_name": "Anne",
                                "zip_code": 12345,
                                "data3":
                                {
                                    "last_name": "Bob",
                                    "first_name": "Shirley"
                                }
                            }
                        }
                        """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(4, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key)  # remove the record ID to compare against the expected dict

        self.assertEqual(self.base_dict, parsed_res)

    def test_parse_data_complex_structure_2(self):
        """
        Tests a complex structure where the first_name is nested, and in a second dictionary entry on the same level,
        verifying that we correctly skip the dictionary with the unimportant data to return the correct data
        """
        input_data = """
                        {
                            "data":
                            {
                                "middle_name": "Rivera",
                                "last_name": "Anne",
                                "data2":
                                {
                                    "last_name": "Sam",
                                    "middle_name": "Elise"
                                },
                                "data3":
                                {
                                    "last_name": "Bob",
                                    "first_name": "Shirley"
                                },
                                "data4":
                                {
                                    "last_name": "Lisa",
                                    "first_name": "Morning"
                                }
                            }
                        }
                        """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(3, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key)  # remove the record ID to compare against the expected dict

        self.base_dict["zip_code"]=""
        self.assertEqual(self.base_dict, parsed_res)

    def test_parse_data_complex_structure_3(self):
        """
        Tests the case where there are two first_name entries, but one of them is empty. The expectation is that
        we'll ignore the empty one, and return the entry with a value
        """
        input_data = """
                        {
                            "zip_code":
                                [
                                    12345,
                                    "two",
                                    "three"
                                ],
                            "data":
                            {
                                "middle_name": "Rivera",
                                "last_name": "Anne",
                                "data3":
                                {
                                    "last_name": "Bob",
                                    "first_name": ""
                                },
                                "data4":
                                {
                                    "last_name": "Bob",
                                    "first_name": "Shirley"
                                }
                            }
                        }
                        """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(4, field_count)

        self.assertIn(process_json.record_id_key, parsed_res)
        parsed_res.pop(process_json.record_id_key)  # remove the record ID to compare against the expected dict

        self.assertEqual(self.base_dict, parsed_res)

    def test_parse_data_complex_structure_no_data(self):
        """
        Tests a complex data structure where the requested data is nowhere to be found, expecting it to return no fields found
        """
        input_data = """
                        {
                            "adata":
                                [
                                    "one",
                                    "two",
                                    "three"
                                ],
                            "data": {
                                "test": "Rivera",
                                "test2": "Anne",
                                "data2":
                                {
                                    "test2": "Sam",
                                    "test3": "Elise"
                                },
                                "data3":
                                {
                                    "test2": "Bob",
                                    "test3": "Shirley"
                                },
                                "data4":
                                {
                                    "test2": "Lisa",
                                    "test3": "Morning"
                                }
                            }
                        }
                        """
        field_count, parsed_res = run_parse_data_on_string(input_data)
        self.assertEqual(0, field_count)
        self.assertIn(process_json.record_id_key, parsed_res)