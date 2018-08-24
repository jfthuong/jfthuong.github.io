#!python

##############
# HOW TO RUN #
##############
#1. Install Nose Tests
'pip install nose'
#2. Run Tests
'nosetests -sv --with-doctest'
##############


import nose
from nose import with_setup
from nose.tools import *

import airlines
from processRecords import *

#Function to check equality and return expected/obtained values if error:
def assert_eq(obt, exp):
	assert obt==exp, "\n*Expected:\n%s\n*Obtained:\n%s" % (exp, obt)


#Test class "Airline_record"
class test_01_Airline_record(object):
	"""Test class 'Airline_record'"""
	#Start and End (displayed with option '-s')
	@classmethod
	def setup_class(self): 
		print ("\nTesting class 'Airline_record' - START")
		self.data={}
			
	@classmethod
	def teardown_class(self): print ("Testing class 'Airline_record' - END\n")
	
	def test_01_init(self):
		'''	Initialisation of class Airline_record'''
		self.data['SQ']=airlines.Airline_record("Singapore Airlines", "SQ")
		assert_eq ( self.data['SQ'].flights, {} )
		assert_eq ( self.data['SQ'].destination, {} )
		assert_eq ( self.data['SQ'].name, "Singapore Airlines" )
		assert_eq ( self.data['SQ'].code, "SQ" )
		self.data['MU']=airlines.Airline_record("China Eastern", "MU")

	def test_02_add_info(self):
		'''Add record to list of flights'''
		self.data['SQ'].add_info({'date':'2015-08-20','time':'08:05','code':'SQ827','destination':'Singapore','take-off':'09:08'})
		assert_eq ( self.data['SQ'].flights, {'SQ827':[{'date':'2015-08-20','delay':63,'time':'08:05'}]} )
		assert_eq ( self.data['SQ'].destination, {'SQ827':'Singapore'} )
		
		self.data['SQ'].add_info({'date':'2015-08-21','time':'08:05','code':'SQ827',
			'destination':'Singapore','take-off':'08:35'})
		assert_eq ( self.data['SQ'].flights, {'SQ827': 
			[{'date':'2015-08-20','delay':63,'time':'08:05'},{'date':'2015-08-21','delay':30,'time':'08:05'}]})
		assert_eq ( self.data['SQ'].destination, {'SQ827':'Singapore'} )
		
		self.data['MU'].add_info({'date':'2015-08-20','time':'08:20','code':'MU511','destination':'Osaka Kansai','take-off':'8:25'})
		self.data['MU'].add_info({'date':'2015-08-20','time':'08:30','code':'MU721','destination':'Seoul','take-off':'9:30'})
		assert_eq ( self.data['MU'].flights, {'MU511':[{'date':'2015-08-20','delay':5,'time':'08:20'}], 
										   'MU721':[{'date':'2015-08-20','delay':60,'time':'08:30'}]})
		assert_eq ( self.data['MU'].destination, {'MU511':'Osaka Kansai', 'MU721':'Seoul'} )
		
		
	def test_03_get_rating_flight(self):
		'''Get the rating of a given flight'''
		assert_eq ( self.data['SQ'].get_rating_flight('SQ827'), (50,46) )
		assert_eq ( self.data['MU'].get_rating_flight('MU511'), (0,5) )
	
	def test_04_get_rating_airline(self):
		'''Get the rating of the airline'''
		assert_eq ( self.data['SQ'].get_rating_airline(), (50,46) )
		assert_eq ( self.data['MU'].get_rating_airline(), (50,32) )
		
		
#Test main program
class test_02_main(object):
	'''Test main program (processRecords.py)'''
	
	#Start and End (displayed with option '-s')
	@classmethod
	def setup_class(self): 
		print ("\nTesting main program - START")
		self.data={}
			
	@classmethod
	def teardown_class(self): print ("Testing main program - END\n")
	
	
	@raises(IOError)
	def test_01_read_flight_records_robustness(self):
		'''Read flight records from an unknown file'''
		read_flight_records("unknonw.txt")

		
	def test_01_read_flight_records(self):
		'''Read flight records from an existing file'''
		
		self.data['records'] = read_flight_records("mini_record.txt")
		assert_eq ( self.data['records'], [ 
			{'code': 'EK303', 'take-off': '0:41', 'destination': 'Dubai', 'airline': 'Emirates Airlines', 'time': '0:05', 'date': '2015-08-20'},
			{'code': 'MU553', 'take-off': '0:15', 'destination': 'Paris Ch. de Gaulle', 'airline': 'China Eastern Airlines', 'time': '0:05', 'date': '2015-08-20'},
			{'code': 'MU219', 'take-off': '0:45', 'destination': 'Frankfurt', 'airline': 'China Eastern Airlines', 'time': '0:05', 'date': '2015-08-20'}
		] )

		
	def test_02_get_ratings_airlines(self):
		'''Get ratings of airlines based on the records'''
		self.data['airlines_list'] = get_ratings_airlines( self.data['records'] )
		assert_eq ( self.data['airlines_list']['Emirates Airlines'].__dict__, {
				'destination': {'EK303': 'Dubai'}, 
				'flights': {'EK303': [{'date': '2015-08-20', 'delay': 36, 'time': '0:05'}]},
				'code': 'EK', 'name': 'Emirates Airlines'
			} )
		assert_eq ( self.data['airlines_list']['China Eastern Airlines'].__dict__, {
			'destination': {'MU553': 'Paris Ch. de Gaulle', 'MU219': 'Frankfurt'}, 
			'flights': {'MU553': [{'date': '2015-08-20', 'delay': 10, 'time': '0:05'}], 'MU219': [{'date': '2015-08-20', 'delay': 40, 'time': '0:05'}]},
			'code': 'MU', 'name': 'China Eastern Airlines'
		} )


	def test_03_list_sorted_ratings(self):
		'''Sort the airlines and flights based on the chances to be late'''
		self.data['rating_airlines'], self.data['rating_flights'] = list_sorted_ratings(self.data['airlines_list'])
		assert_eq ( self.data['rating_airlines'], [('China Eastern Airlines', 50, 25), ('Emirates Airlines', 100, 36)] )
		assert_eq ( self.data['rating_flights'], [('MU553', 0, 10), ('EK303', 100, 36), ('MU219', 100, 40)] )

		
	def test_04_get_first_last_elem(self):
		'''Return lists with first/last <nb_elem> elements'''
		assert_eq ( get_first_last_elem(self.data['rating_flights'],1)[0], [('MU553', 0, 10)]  )
		assert_eq ( get_first_last_elem(self.data['rating_flights'],1)[1], [('MU219', 100, 40)] )
		
		assert_eq ( get_first_last_elem(self.data['rating_flights'],0)[0], [] )
		assert_eq ( get_first_last_elem(self.data['rating_flights'],0)[1], [] )

		assert_eq ( get_first_last_elem(['f', 'e', 'd', 'c', 'b', 'a'],4)[0], ['f', 'e', 'd', 'c'] )
		assert_eq ( get_first_last_elem(['f', 'e', 'd', 'c', 'b', 'a'],4)[1], ['a', 'b', 'c', 'd'] )
		

if __name__ == "__main__":
	nose.main(argv=['--nocapture', '-v', '--with-doctest'])
