import boto3
import logging
import time

class Textract:
    REGION = "us-east-1"
    logger = logging.getLogger('vara-backend')

    def __init__(self) -> None:
        self.client = boto3.client('textract', region_name=self.REGION)
    
    def start_analysis(self, s3_bucket_name, document_name):
        response = self.client.start_expense_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3_bucket_name,
                    'Name': document_name
                }
            },
        )
        return response['JobId']
    
    def get_job_status(self,job_id):
        time.sleep(1)
        response = self.client.get_expense_analysis(JobId=job_id)
        status = response["JobStatus"]

        while(status == "IN_PROGRESS"):
            time.sleep(1)
            response = self.client.get_expense_analysis(JobId=job_id)
            status = response["JobStatus"]
        return status
    
    def get_job_results(self, job_id):
        doc = []
        time.sleep(1)
        response = self.client.get_expense_analysis(JobId=job_id)
        doc.append(response)
        next_token = None
        if 'NextToken' in response:
            next_token = response['NextToken']

        while next_token:
            time.sleep(1)
            response = self.client.get_expense_analysis(JobId=job_id, NextToken=next_token)
            doc.append(response)
            next_token = None
            if 'NextToken' in response:
                next_token = response['NextToken']
        return doc

    def get_relevant_fields(self, document):
        confidence = 0
        total_field = {}
        for doc in document:
            expense_document = doc['ExpenseDocuments']
            for expense_doc in expense_document:
                summary = expense_doc['SummaryFields']
                for field in summary:
                    if field['Type']['Text']=="TOTAL":
                        if field['Type']['Confidence']>confidence:
                            total_field['FieldName'] = field['LabelDetection']['Text']
                            total_field['Value'] = field['ValueDetection']['Text']
                            confidence = field['Type']['Confidence']
        return total_field

    
    def get_analysis(self, s3_bucket_name, document_name):
        job_id = self.start_analysis(s3_bucket_name, document_name)
        self.logger.info(f'Started job with id: {job_id}')

        job_status = self.get_job_status(job_id)
        if job_status=="SUCCEEDED":
            doc = self.get_job_results(job_id)
        elif job_status=="FAILED":
            return Exception
        return self.get_relevant_fields(doc)
        
