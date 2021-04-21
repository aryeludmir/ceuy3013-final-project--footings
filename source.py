# This file is required. Use the same name, "source.py".
# All of your *foundational* code goes here, meaning the functions and classes
# that can be used to build larger processes. For example, the class you
# created for the OOP assignment would go here.

# Here is a test class, replace the code below with your own
class TestClass:
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return 'number: {}'.format(self.number)