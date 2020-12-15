from unittest import TestCase
import json
import process_json


def run_find_field_on_string(data:str):
    """
    Runs the process_json.find_field on the supplied data string, searching specifically for a "first_name" field

    :param data: a JSON formatted string to be searched
    :return: the results of running find_field for "first_name"
    """
    data_dict = json.loads(data)
    results = process_json.find_field("first_name", data_dict)
    return results


class TestFindField(TestCase):

    def test_find_field_empty_dict(self):
        """
        Tests the case where we pass find_field an empty dictionary
        """
        parsed_res = process_json.find_field("first_name", {})

        self.assertEqual(None,parsed_res)

    def test_find_field_bad_input_none(self):
        """
        Tests the case where we pass find_field None
        """
        parsed_res = process_json.find_field("first_name", None)

        self.assertEqual(None, parsed_res)

    def test_find_field_bad_input_list(self):
        """
        Tests the case where we pass find_field a list
        """
        parsed_res = process_json.find_field("first_name", ["Shirley", "Bob"])

        self.assertEqual(None, parsed_res)

    def test_find_field_bad_input_empty_string(self):
        """
        Tests the case where we pass find_field None
        """
        parsed_res = process_json.find_field("first_name", "")

        self.assertEqual(None, parsed_res)

    def test_find_field(self):
        """
        Tests the most basic case of find_field, where the first name is at the top level of the supplied json
        """
        input_data = """
        {
            "middle_name": "Rivera",
            "first_name": "Shirley", 
            "last_name": "Anne", 
            "zip_code": 12345
        }
        """
        parsed_res = run_find_field_on_string(input_data)
        self.assertEqual("Shirley",parsed_res)

    def test_find_field_nested_dict(self):
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
        parsed_res = run_find_field_on_string(input_data)

        self.assertEqual("Shirley", parsed_res)

    def test_find_field_multiple_entries(self):
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
        parsed_res = run_find_field_on_string(input_data)

        self.assertEqual("Shirley",parsed_res)

    def test_find_field_list(self):
        """
        Tests the case where first_name is a list of items, and expecting the find_field to pull the first one
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
        parsed_res = run_find_field_on_string(input_data)

        self.assertEqual("Shirley",parsed_res)

    def test_find_field_nested_list(self):
        """
        Test the case where first_name is in a nested list, verifying that we recurse and return a list item correctly
        """
        input_data = """
                        {
                            "data":
                            {
                                "first_name":
                                [
                                    "Shirley",
                                    "Rivera",
                                    "Anne"
                                ]
                            }
                        }
                        """
        parsed_res = run_find_field_on_string(input_data)
        self.assertEqual("Shirley",parsed_res)

    def test_find_field_complex_structure_1(self):
        """
        Tests a more complex structure, where the first_name is nested well into the second element, verifying
        recursion and >1 element structures
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
        parsed_res = run_find_field_on_string(input_data)
        self.assertEqual("Shirley",parsed_res)

    def test_find_field_complex_structure_2(self):
        """
        Tests a complex structure where the first_name is nested, and in a second dictionary entry on the same level,
        verifying that we correctly skip the dictionary with the unimportant data to return the correct data
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
        parsed_res = run_find_field_on_string(input_data)
        self.assertEqual("Shirley",parsed_res)

    def test_find_field_complex_structure_3(self):
        """
        Tests the case where there are two first_name entries, but one of them is empty. The expectation is that
        we'll ignore the empty one, and return the entry with a value
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
        parsed_res = run_find_field_on_string(input_data)
        self.assertEqual("Shirley",parsed_res)

    def test_find_field_complex_structure_no_data(self):
        """
        Tests a complex data structure where the requested field is nowhere to be found, expecting it to return None
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
                                    "middle_name": "Shirley"
                                },
                                "data4":
                                {
                                    "last_name": "Lisa",
                                    "middle_name": "Morning"
                                }
                            }
                        }
                        """
        parsed_res = run_find_field_on_string(input_data)
        self.assertEqual(None, parsed_res)