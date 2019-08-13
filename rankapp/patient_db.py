from interface import implements, Interface
import pandas as pd
import pyodbc
from flask import current_app

class I_PatientData(Interface):

    def returnPatientDf(self):
        pass

class DummyPatientData(implements(I_PatientData)):

    def __init__(self):

        self.df = pd.DataFrame()
        self.df['Name'] = ['Paul Stephenson', 'Princess Campbell', 'Guy Bailey', 
            		      'Roy Hackett', 'Carmen Beckford', 'Prince Brown', 
            		      'Owen Henry', 'Pero Jones', 'James Peters', 'Alfred Fagon',
                          'Paula Stephenson', 'Prince Campbell', 'Gina Bailey', 
            		      'Rachel Hackett', 'Chris Beckford', 'Princess Brown', 
            		      'Ofelia Henry', 'Phoebe Jones', 'Jennie Peters', 'Alice Fagon']
        self.df['Bed'] = [1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21]
        self.df['T_number'] = ['T38746', 'T18346', 'T32985', 'T23190', 'T19583',
                                'T49568', 'T30297', 'T43078', 'T89765', 'T34287',
                                'T36342', 'T28447', 'T51182', 'T43325', 'T56501',
                                'T26504', 'T79265', 'T91053', 'T16095', 'T57232']
        self.df['Age'] = ['61', '52', '81', '77', '65', '82', '80', '59', '38', '76',
                           '64', '50', '84', '72', '63', '89', '85', '51', '37', '74']
        self.df['Admission'] = ['2019/01/25', '2019/03/01', '2019/02/18', '2019/02/22', 
                                '2019/02/15', '2019/02/24', '2019/03/02', '2019/02/21', '2019/02/28', '2019/02/29',
                                '2019/03/25', '2019/04/01', '2019/03/18', '2019/03/22', 
                                '2019/03/15', '2019/03/24', '2019/04/02', '2019/03/21', '2019/03/28', '2019/03/29']
        
        self.df['DischargeStatus'] = ['-' for i in self.df['Name']]

    def returnPatientDf(self):
        return self.df

class IccaPatientData(implements(I_PatientData)):
## This class will get the current patients from ICCA using pyodbc:
    def __init__(self):

        self.df = pd.DataFrame()
        self.queryDatabase()

    def returnPatientDf(self):
        return self.df

    def queryDatabase(self):
        try:

            server = "ubhnt455.ubht.nhs.uk"
            database = "CISReportingDB"
            tc ="yes"  

            cnxn = pyodbc.connect('trusted_connection='+tc+';DRIVER={SQL Server};SERVER='+server+';DATABASE='+database)
            cursor = cnxn.cursor()

            cursor.execute("""SELECT TOP 23 D.firstName, D.lastName, D.lifeTimeNumber, DATEDIFF(hour, D.dateOfBirth, GETDATE())/8766 AS Age, B.bedLabel, CONVERT(date, P.inTime) 
               FROM PtCensus P
               INNER JOIN D_Encounter D
               ON P.encounterId=D.encounterId 
               INNER JOIN PtBedStay B
               ON P.encounterId=B.encounterId 
               WHERE P.clinicalUnitId=5 and P.outTime IS NULL and B.outTime IS NULL
               ORDER BY P.inTime desc;""")    

            names = []
            beds = []
            numbers = []
            ages = []
            admissions = []

            row = cursor.fetchone()
            while row:
                #print(row)
                names.append(row[0] + " " + row[1])
                beds.append(row[4])
                numbers.append(row[2])
                ages.append(row[3])
                admissions.append(row[5])

                row =cursor.fetchone()

            cursor.close()
            del cursor
            cnxn.close()

            self.df['Name'] = names
            self.df['Bed'] = beds
            self.df['T_number'] = numbers
            self.df['Age'] = ages
            self.df['Admission'] = admissions
            self.df['Discharge to'] = ['-' for i in self.df['Name']]
            
        except:
            print("Error: Could not connect to database.")
