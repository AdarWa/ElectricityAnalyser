import re
import datetime
import pandas
import config

pattern = re.compile(r'^"\d{2}/\d{2}/\d{4}","\d{2}:\d{2}",[-+]?\d*\.?\d+$')

def open_csv(path):
    f = open(path, 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    first_line = 0
    for i, line in enumerate(lines):
        if pattern.match(line):
            first_line = i
            break
    lines = lines[first_line:]
    data = []
    for line in lines:
        line = line.strip()
        parts = line.split(',')
        if len(parts) != 3:
            continue
        date = parts[0].strip('"')
        time = parts[1].strip('"')
        dt = datetime.datetime.strptime(date + ' ' + time, '%d/%m/%Y %H:%M')
        kwh = float(parts[2])
        data.append((dt, kwh))
    df = pandas.DataFrame(data, columns=['datetime', 'kWh'])
    df['datetime'] = pandas.to_datetime(df['datetime'])
    df['kWh'] = df['kWh'].astype(float)
    df = df.sort_values(by='datetime')
    df.reset_index(drop=True, inplace=True)
    return df

def group_by_time(df):
    df['date'] = df['datetime'].dt.date
    df['time'] = df['datetime'].dt.time
    return df.groupby('time')["kWh"].mean()

def apply_plan(df, planName):
    for i,row in df.items():
        time = i
        plan = next((p for p in config.getConfig()['plans'] if p['name'] == planName), None)
        if plan is None:
            raise ValueError(f"Plan '{planName}' not found")
        if time.hour in plan["hours"]:
            df[i] *= 1-plan['discount']
    return df
