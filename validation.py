import pandas as pd
import uuid
import boto3
import pickle
import io
import os

class validation_synth:
    
    """ This class is responsible for validating the synthetic dataset compared to the real one
    The constructor needs two inputs when creating the object, namely: 
    the real dataset and the synthetic dataset with this order. """
    
    def __init__(self, origdst, synthdst):
        
        self.origdst = origdst
        self.synthdst = synthdst
        
    def check_tan(self):
        
        """ This method is responsible for checking whether there are same customer ids between the two datasets. """
        
        flag = False

        if (set(self.origdst['TAN'].unique()) & set(self.synthdst['TAN'].unique())):
            flag = True
        else:
            print('TAN check: Success - There are no same customer IDs between the two sets')
            
        return flag
    
    def check_counts(self):
        
        """ This method examines if the synthetic dataset fulfills the constraint about returning 
        10 or more customer id counts when grouping by the demographic attributes. """

        flag = False

        cols = (list(self.synthdst.columns[12:]))
        cols.append('TAN')

        synth = self.synthdst

        d = synth.groupby(cols)['TAN'].size().reset_index(name='counts').sort_values(by='counts', ascending=True)

        counts = list(d['counts'].unique())

        if all(i >= 10 for i in counts):
            print('Counts check: Success - The dataset fulfils the constraint regarding TAN counts')
        else:
            print('Counts check: Error - The dataset appears to be problematic.\nThe minimum TAN counts should be greater than or equal to 10.')
            print('The minimum count value is', min(counts))
            flag = True

        return flag
            
    def check_dtypes(self):
        
        """ This method checks whether the columns of the real dataset and the synthetic data are of the same data type. """
        
        dtps = (self.origdst.dtypes == self.synthdst.dtypes)

        flag = False
        
        if dtps.all():
            print('Data types check - Success, the data types among the columns are the same')
        else:
            
            dfdt = (self.origdst.dtypes == self.synthdst.dtypes).reset_index(name='fcounts')
            flst = list(dfdt[dfdt['fcounts'] == False].index)
            colms = list(dfdt['index'])
            
            print('Data types check: Error - the data types among the columns are NOT the same')
            print('The columns with not the same data type are:',[colms[item] for item in flst])

            flag = True

        return flag
    
    def validate(self):
        
        """ This method is to be called after creating the instance from the class """
        
        fl = True
        
        try:
            fl = self.check_tan()
        except:
            print('Error during TAN check')
            
        if fl:
            print('TAN check: Error - There are same customer IDs between the two sets')
            
        else:
            try:
                fl = self.check_dtypes()
            except:
                print('Error while checking data types')

            if fl:
                print('Incorrect datatypes for certain attributes')

            else:
                try:
                    fl = self.check_counts()

                except:
                    print('Error while checking TAN counts')

        return fl

if __name__ == "__main__":
    # Set up access to s3
    s3 = boto3.resource('s3')
    s3_bucket = os.environ['data_bucket']

    # Read in the original data from s3
    try:
        og_file_key = os.environ['og_file_key']
        df_og = pickle.loads(s3.Bucket(s3_bucket).Object(og_file_key).get()['Body'].read())
        print("Succeeded in loading original data from s3 bucket")
    except:
        print("Error while loading original data from s3 bucket")

    # Read in the synthetic data from s3
    try:
        syn_file_key = os.environ['syn_file_key']
        df_syn = pickle.loads(s3.Bucket(s3_bucket).Object(syn_file_key).get()['Body'].read())
        print("Succeeded in loading synthetic data from s3 bucket")
    except:
        print("Error while loading synthetic data from s3 bucket")
    # df_syn = pd.read_pickle('viewership_demographics/viewership_data_rehashed_TAN.pkl')

    # df_og.reset_index(drop=True, inplace=True)
    # import hashlib
    # for i in range(len(df_og)):
    #     df_og.TAN[i] = hashlib.md5(df_og.TAN[i].encode("utf-8")).hexdigest()[0:16]
    #the parameters should be: the real dataset and then the synthetic dataset
    print("Validating synthetic data...")
    obj = validation_synth(df_og,df_syn)
    validate_flag = obj.validate()

    if validate_flag==False:
        # move to output bucket of vendor
        print("Validation synthetic data success. Moving to vendor-output-bucket")
        #pickle_buffer = pickle.dumps(df_syn)
        #s3.Object(bucket_name=vendor_bucket, key='df_syn.pkl').put(Body=pickle_buffer)
        # delete from data-team bucket
    else:
        print("Validation synthetic data failure.")
        # write text file to