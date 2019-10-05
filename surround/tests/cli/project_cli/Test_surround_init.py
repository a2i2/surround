import unittest
import subprocess
import shutil
import os

class MyTestCase(unittest.TestCase):

    #validating the surround init command line functionality
    #verfiying the output after the surround init command
    def check_project_name(self):
        self.test_surround_init()#for checking the Name of project input
        self.test_surround_init_lowercase('tempor','temporary') #for testing the lowercase for project name-successfuly created
        self.test_surround_init_lowercase_number('tempor123','temporary')#for testing the project name with lowercase and numbers
        self.test_surround_init_lowercase_underscore('temporary_','temporary')#for testing the project name with lowercase & Underscore
        self.test_surround_init_lowercase_symbol('temporary*#','temporary')#for testing the project name with lowercase&symbols
        self.test_surround_init_onlysymbol(',#*@$','temporary')#for testing the project name with symbols
        self.test_surround_uppercase('SURROUNDINIT')#for testing the project name with symbols
        self.test_total_surround_files()#for validating total no of files inside the surround environment
        self.test_created_surround_files()#for validating the created file names of surround project to the actual file name


    def test_surround_init(self):
        process1= subprocess.run(["surround", "init"], encoding='utf-8', stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        print("Output captured:", process1.stdout)
        self.assertIn(process1.stdout,"Name of project: ")

    def test_surround_init_lowercase(self,name='tempor',description='temporary'):
        process = subprocess.run(["surround", "init",'-p',name,'-d',description,'-w','no'], encoding='utf-8',
                                 stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        print("Output captured:", process.stdout[:25])
        self.assertIn(process.stdout[:25], "info: project created at ")
        self.assertTrue(os.path.exists("tempor"))
        shutil.rmtree('tempor')

    def test_surround_init_lowercase_underscore(self,name='temporary_',description='temporary'):
        process = subprocess.run(["surround", "init", '-p', name, '-d', description, '-w', 'no'], encoding='utf-8',
                                 stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("Output captured:", process.stdout[:25])
        self.assertIn(process.stdout[:25], "info: project created at ")
        self.assertTrue(os.path.exists("temporary_"))
        shutil.rmtree('temporary_')


    def test_surround_init_lowercase_symbol(self,name='temporary*#',description='temporary'):
        process = subprocess.run(["surround", "init", '-p',name,'-d',description,'-w','no'], encoding='utf-8',
                                 stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("Output captured:", process.stdout)
        self.assertIn(process.stdout, " surround: error: Name user# must be lowercase letters ")

    def test_surround_init_only_symbol(self,name=',#*@$',description='temporary'):
        process = subprocess.run(["surround", "init", '-p',name, '-d',description, '-w', 'no'], encoding='utf-8',
                                 stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("Output captured:", process.stdout)
        self.assertIn(process.stdout, " surround: error: Name #*@$' must be lowercase letters ")

    def test_surround_init_lowercase_number(self,name='tempor123',descpription='temporary'):
        process = subprocess.run(["surround", "init", '-p',name,'-d',descpription,'-w','no'], encoding='utf-8',
                                 stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("Output captured:", process.stdout)
        self.assertIn(process.stdout, " surround: error: Name user123 must be lowercase letters ")
    def test_surround_uppercase(self,name='SURROUNDINIT'):
        process = subprocess.run(['surround','init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name SURROUNDINIT must be lowercase letters ")

    def test_surround_uppercasewithnumber(self,name='SURROUNDINIT123'):
        process = subprocess.run(['surround','init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name SURROUNDINIT123 must be lowercase letters  ")

    def test_surround_uppercasewithunderscore(self,name='SURROUNDINIT_123'):
        process = subprocess.run(['surround','init', '-p',name ], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name SURROUNDINIT_123 must be lowercase letters ")

    def test_surround_uppercasewithsymbol(self,name='SURROUNDINIT*'):
        process = subprocess.run(['surround','init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name SURROUNDINIT* must be lowercase letters ")

    def test_surround_lowercase_underscore_number(self,name='surroundinit_123'):
        process = subprocess.run(['surround','init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name SURROUNDINIT_123 must be lowercase letters ")

    def test_surround_Uppercase_underscore_number(self,name='SURROUND_123'):
        process = subprocess.run(['surround','init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name SURROUND_123 must be lowercase letters ")

    def test_surround_onlynumber(self,name='123'):
        process = subprocess.run(['surround','init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout, "surround: error: Name 123 must be lowercase letters ")

    def test_surround_underscore_number(self, name='_123'):
        process = subprocess.run(['surround', 'init', '-p', name], encoding='utf-8', stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE)
        print("captured output is ", process.stdout)
        self.assertIn(process.stdout,"surround: error: Name _123 must be lowercase letters ")

      # Testing the files in surround project
    def test_total_surround_files(self):
        subprocess.run(["surround", "init", '-p', 'temporary', '-d', 'temporary', '-w', 'no'],
                                 encoding='utf-8',
                                 stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        x=len(os.listdir('temporary'))
        print(os.listdir('temporary'))
        print(x)
        self.assertEquals(x,15)                         #comparing the total number of files created in surround
        shutil.rmtree('temporary')
    def test_created_surround_files(self):
        subprocess.run(["surround", "init", '-p', 'temporary', '-d', 'temporary', '-w', 'no'],
                       encoding='utf-8',
                       stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        x=os.listdir('temporary')
        expected = ['.gitignore', '.surround', 'data', 'Dockerfile', 'docs', 'dodo.py', 'models', 'notebooks', 'output',
                    'README.md',
                    'requirements.txt', 'scripts', 'spikes', 'temporary', 'tests']
        for i in range(len(expected)):
            self.assertIn(expected[i], x[i])            #Checking the actual filename with the generated file names of the project
        print("test is successful")
        shutil.rmtree('temporary')

if __name__ == '__main__':
    unittest.main()
