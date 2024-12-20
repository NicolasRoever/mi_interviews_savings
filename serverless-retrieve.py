from boto3 import resource
from pandas import DataFrame
from argparse import ArgumentParser


def retrieve_all_sessions(table_name:str, output_path:str, print_chats:bool=False):
    """ 
    Retrieve chat history (list of dicts) for all sessions (list of dicts).

    Returns
        chats: (list) of "long" form data with one session-message per row, e.g.
            [
                {'session_id':101, 'time':0, 'role':'interviewer', 'message':'Hello', ...}
                {'session_id':101, 'time':1, 'role':'respondent', 'message':'World', ...}
                ...
            ]
    """
    table = resource('dynamodb').Table(table_name)

    chats = []
    last_eval = None
    while True:
        # Handle multiple chunks with contiguous scan
        resp = table.scan(ExclusiveStartKey=last_eval) if last_eval else table.scan()
        chats.extend([
            message for session in resp.get('Items',[]) for message in session['chat']
        ])
        if not resp.get('LastEvaluatedKey'): break
        last_eval = resp['LastEvaluatedKey']

    # Save to CSV
    DataFrame(chats).to_csv(output_path)
    if print_chats: 
        for chat in chats:
            print(chat)
    return
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--table_name', type=str, help="Name of DynamoDBTable")
    parser.add_argument('--output_path', type=str, default="chats.csv", help="Filepath to chats CSV")
    args = parser.parse_args()
    retrieve_all_sessions(args.table_name, args.output_path)