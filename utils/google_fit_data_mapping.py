# maps google fit data types to timescaledb tables
# list all available google fit data types and map them to a personicle data type
# this mapping will keep evolving with new and custom data types

EVENTS_DICTIONARY = {
    9: "com.personicle.individual.events.exercise.Aerobics",
    119: "com.personicle.individual.events.exercise.Archery",
	10: "com.personicle.individual.events.exercise.Badminton",
	11: "com.personicle.individual.events.exercise.Baseball",
	12: "com.personicle.individual.events.exercise.Basketball",
	13: "com.personicle.individual.events.exercise.Biathlon",
	1: "com.personicle.individual.events.exercise.Biking",
	14: "com.personicle.individual.events.exercise.Handbiking",
	15: "com.personicle.individual.events.exercise.Biking.Mountain_biking",
	16: "com.personicle.individual.events.exercise.Biking.Road_biking",
	17: "com.personicle.individual.events.exercise.Biking.Spinning",
	18: "com.personicle.individual.events.exercise.Biking.Stationary_biking",
	19: "com.personicle.individual.events.exercise.Biking.Utility_biking",
	20: "com.personicle.individual.events.exercise.Boxing",
	21: "com.personicle.individual.events.exercise.Calisthenics",
	22: "com.personicle.individual.events.exercise.Circuit_training",
	23: "com.personicle.individual.events.exercise.Cricket",
	113: "com.personicle.individual.events.exercise.Crossfit",
	106: "com.personicle.individual.events.exercise.Curling",
	24: "com.personicle.individual.events.Dancing",
	102: "com.personicle.individual.events.Diving"
# Elevator	117
# Elliptical	25
# Ergometer	103
# Escalator	118
# Fencing	26
# Football (American)	27
# Football (Australian)	28
# Football (Soccer)	29
# Frisbee	30
# Gardening	31
# Golf	32
# Guided Breathing	122
# Gymnastics	33
# Handball	34
# HIIT	114
# Hiking	35
# Hockey	36
# Horseback riding	37
# Housework	38
# Ice skating	104
# In vehicle	0
# Interval Training	115
# Jumping rope	39
# Kayaking	40
# Kettlebell training	41
# Kickboxing	42
# Kitesurfing	43
# Martial arts	44
# Meditation	45
# Mixed martial arts	46
# Other (unclassified fitness activity)	108
# P90X exercises	47
# Paragliding	48
# Pilates	49
# Polo	50
# Racquetball	51
# Rock climbing	52
# Rowing	53
# Rowing machine	54
# Rugby	55
# Running	8
# Jogging	56
# Running on sand	57
# Running (treadmill)	58
# Sailing	59
# Scuba diving	60
# Skateboarding	61
# Skating	62
# Cross skating	63
# Indoor skating	105
# Inline skating (rollerblading)	64
# Skiing	65
# Back-country skiing	66
# Cross-country skiing	67
# Downhill skiing	68
# Kite skiing	69
# Roller skiing	70
# Sledding	71
# Snowboarding	73
# Snowmobile	74
# Snowshoeing	75
# Softball	120
# Squash	76
# Stair climbing	77
# Stair-climbing machine	78
# Stand-up paddleboarding	79
# Still (not moving)	3
# Strength training	80
# Surfing	81
# Swimming	82
# Swimming (open water)	84
# Swimming (swimming pool)	83
# Table tennis (ping pong)	85
# Team sports	86
# Tennis	87
# Tilting (sudden device gravity change)	5
# Treadmill (walking or running)	88
# Unknown (unable to detect activity)	4
# Volleyball	89
# Volleyball (beach)	90
# Volleyball (indoor)	91
# Wakeboarding	92
# Walking	7
# Walking (fitness)	93
# Nording walking	94
# Walking (treadmill)	95
# Walking (stroller)	116
# Waterpolo	96
# Weightlifting	97
# Wheelchair	98
# Windsurfing	99
# Yoga	100
# Zumba	101
}


DATA_DICTIONARY = {
    # Activity data types
    "com.google.calories.bmr": "com.personicle.individual.datastreams.resting_calories",
    "com.google.calories.expended": "com.personicle.individual.datastreams.total_calories",
    "com.google.cycling.pedaling.cadence": "com.personicle.individual.datastreams.cycling.cadence",
    "com.google.cycling.pedaling.cumulative": "com.personicle.individual.datastreams.cycling.cumulative_cadence",
    "com.google.heart_minutes": "com.personicle.individual.datastreams.heart_intensity_minutes",
    "com.google.active_minutes": "com.personicle.individual.datastreams.active_minutes",
    "com.google.power.sample": "com.personicle.individual.datastreams.cycling.power",
    "com.google.step_count.cadence": "com.personicle.individual.datastreams.step.cadence",
    "com.google.step_count.delta": "com.personicle.individual.datastreams.step.count",
    "com.google.step_count.cumulative": "com.personicle.individual.datastreams.step.cumulative",
    # different exercise performed in a workout, should be stored as events in the personicle
    # "com.google.activity.exercise": "personal_events",
    # "com.google.activity.segment": "personal_events",

    # Body data types
    "com.google.body.fat.percentage": "com.personicle.individual.datastreams.body_fat",
    "com.google.heart_rate.bpm": "com.personicle.individual.datastreams.heartrate",
    "com.google.height": "com.personicle.individual.datastreams.height",
    "com.google.weight": "com.personicle.individual.datastreams.weight",

    # Location data types
    "com.google.cycling.wheel_revolution.rpm": "com.personicle.individual.datastreams.cycling.cadence",
    "com.google.cycling.wheel_revolution.cumulative": "com.personicle.individual.datastreams.cycling.cumulative_cadence",
    "com.google.distance.delta": "com.personicle.individual.datastreams.distance",
    # "com.google.location.sample": "location",
    "com.google.speed": "com.personicle.individual.datastreams.speed",

    # Nutrition data types
    # "com.google.hydration": "water_intake",
    # meal event from google fit
    # "com.google.nutrition": "food_event"

    # Sleep data types
    "com.google.sleep.segment": "sleep_stage",

    #Health data types
    "com.google.blood_glucose": "com.personicle.individual.datastreams.blood_glucose",
    # "com.google.blood_pressure": "blood_pressure",
    # "com.google.body.temperature": "body_temperature",
    # "com.google.cervical_mucus": "cervical_mucus",
    # "com.google.cervical_position": "cervical_position",
    # "com.google.menstruation": "menstruation",
    # "com.google.ovulation_test": "ovulation_test",
    # "com.google.oxygen_saturation": "blood_oxygen_saturation",
    # "com.google.vaginal_spotting": "vaginal_spotting"

}