import analyser

def test_open_csv():
    df = analyser.open_csv('test.csv')
    
    return analyser.group_by_time(df).to_dict()

if __name__ == '__main__':
    print(test_open_csv())
    print("Test completed successfully.")