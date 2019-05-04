"""
This file handles generating appropriate notifications from the latest air
pollution data
"""

# Import the air pollution data
while True:
    try:
        air_pollution = pd.read_csv("./data/air-pollution-data.csv")
        break
    except:
        print ('File does not exist yet, waiting 30 secs before retrying')
        time.sleep(30)

"""
Assumptions:
- Times are taken on the hour.
- The average level changes hourly.
"""
# Logic to handle triggering notifications on each of the three topics
