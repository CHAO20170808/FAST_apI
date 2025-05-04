import pytest

def test_equal():
    assert 1 == 1, "Test failed: 1 is not equal to 1"
    assert 3 != 1, "Test failed: 3 is equal to 1"

def test_not_equal():
    assert 3 >= 2, "Test failed: 3 not is equal to 2"    

def test_is_instance():
    assert isinstance(3, int), "Test failed: 3 is not an instance of int"
    assert isinstance("hello", str), "Test failed: 'hello' is not an instance of str"

def test_is_bool():
    assert isinstance(True, bool), "Test failed: True is not an instance of bool"
    assert isinstance(False, bool), "Test failed: False is not an instance of bool"

def test_type():
    assert isinstance(5,int), "Test failed: 5 is a int"
    assert isinstance(5.8,float)    

def test_list_test():
    my_list = [1, 2, 3]
    assert isinstance(my_list, list), "Test failed: my_list is not a list"
    assert len(my_list) == 3, "Test failed: Length of my_list is not 3"
    assert my_list[0] == 1, "Test failed: First element of my_list is not 1"    

class TempClass:
    def __init__(self, first_name: str, last_name: str,major:str, age: int):    
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.age = age

def test_person_initialization():
    p= TempClass("ken", "le", "Computer Science", 20)
    assert p.first_name == "ken", "Test failed: first_name is not 'ken'"
    assert p.last_name == "le", "Test failed: last_name is not 'le'"
    assert p.major == "Computer Science", "Test failed: major is not 'Computer Science'"
    assert p.age == 20, "Test failed: age is not 20"

@pytest.fixture
def wantih_employee():
    return TempClass("Ian", "Chen", "IT Science", 32)

def test_employee_details(wantih_employee):
    assert wantih_employee.first_name == "Ian"
    assert wantih_employee.major == "IT Science"
    assert wantih_employee.age > 30 