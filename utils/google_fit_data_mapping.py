from .google_fit_parsers import *

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
	102: "com.personicle.individual.events.Diving",
	8: "com.personicle.individual.events.Running",
	72: "com.personicle.individual.events.Sleep",
	53: "com.personicle.individual.events.Rowing",
	54: "com.personicle.individual.events.RowingMachine",
    117: "com.personicle.individual.events.Elevator",
    25: "com.personicle.individual.events.Elliptical",
    103: "com.personicle.individual.events.Erogometer",
    118: "com.personicle.individual.events.Escalator",
    26: "com.personicle.individual.events.Fencing",
    27: "com.personicle.individual.events.FootBallAmerican",
    28: "com.personicle.individual.events.FootballAustralian",
    29: "com.personicle.individual.events.FootballSoccer",
    30: "com.personicle.individual.events.Frisbee",
    31: "com.personicle.individual.events.Gardening",
    32: "com.personicle.individual.events.Golf",
    122: "com.personicle.individual.events.GuidedBreathing",
    33: "com.personicle.individual.events.Gymnastics",
    34: "com.personicle.individual.events.Handball",
    114: "com.personicle.individual.events.HIIT",
    35: "com.personicle.individual.events.Hiking",
    36: "com.personicle.individual.events.Hockey",
    37: "com.personicle.individual.events.HorsebackRiding",
    38: "com.personicle.individual.events.Housework",
    104: "com.personicle.individual.events.IceSkating",
    0: "com.personicle.individual.events.InVehicle",
    115: "com.personicle.individual.events.IntervalTraining",
    39: "com.personicle.individual.events.JumpingRope",
    40: "com.personicle.individual.events.Kayaking",
    41: "com.personicle.individual.events.KettlebellTraining",
    42: "com.personicle.individual.events.Kickboxing",
    43: "com.personicle.individual.events.Kitesurfing",
    44: "com.personicle.individual.events.MartialArts",
    45: "com.personicle.individual.events.Meditatation",
    46: "com.personicle.individual.events.MixedMartialArts",
    108: "com.personicle.individual.events.other",
    47: "com.personicle.individual.events.P90X",
    48: "com.personicle.individual.events.Paragliding",
    49: "com.personicle.individual.events.Pilates",
    50: "com.personicle.individual.events.Polo",
    51: "com.personicle.individual.events.Racquetball",
    52: "com.personicle.individual.events.other",
    55: "com.personicle.individual.events.Rugby",
    56: "com.personicle.individual.events.Jogging",
    57: "com.personicle.individual.events.RunningOnSand",
    58: "com.personicle.individual.events.RunningTreadmill",
    59: "com.personicle.individual.events.Sailing",
    60: "com.personicle.individual.events.ScubaDiving",
    61: "com.personicle.individual.events.Skateboarding",
    62: "com.personicle.individual.events.Skating",
    63: "com.personicle.individual.events.CrossSkating",
    105: "com.personicle.individual.events.IndoorSkating",
    64: "com.personicle.individual.events.InlineSkating",
    65: "com.personicle.individual.events.Skiing",
    66: "com.personicle.individual.events.BackCountrySkiing",
    67: "com.personicle.individual.events.CrossCountrySkiing",
    68: "com.personicle.individual.events.DownhillSkiing",
    69: "com.personicle.individual.events.KiteSkiing",
    70: "com.personicle.individual.events.RollerSkiing",
    71: "com.personicle.individual.events.Sledding",
    73: "com.personicle.individual.events.Snowboarding",
    74: "com.personicle.individual.events.Snowmobile",
    75: "com.personicle.individual.events.Snowshoeing",
    120: "com.personicle.individual.events.Softball",
    76: "com.personicle.individual.events.Squash",
    77: "com.personicle.individual.events.StairClimbing",
    78: "com.personicle.individual.events.StairClimbingMachine",
    79: "com.personicle.individual.events.StandupPaddleboarding",
    80: "com.personicle.individual.events.StrengthTraining",
    81: "com.personicle.individual.events.Surfing",
    82: "com.personicle.individual.events.Swimming",
    83: "com.personicle.individual.events.SwimmingPool",
    84: "com.personicle.individual.events.SwimmingOpenWater",
    85: "com.personicle.individual.events.TableTennis",
    86: "com.personicle.individual.events.TeamSports",
    87: "com.personicle.individual.events.Tennis",
    5: "com.personicle.individual.events.Tilting",
    88: "com.personicle.individual.events.Treadmill",
    4: "com.personicle.individual.events.Unknown",
    89: "com.personicle.individual.events.Volleyball",
    90: "com.personicle.individual.events.VolleyballBeach",
    91: "com.personicle.individual.events.VolleyballIndoor",
    92: "com.personicle.individual.events.Wakeboarding",
    7: "com.personicle.individual.events.Walking",
    93: "com.personicle.individual.events.WalkingFitness",
    94: "com.personicle.individual.events.NordicWalking",
    95: "com.personicle.individual.events.WalkingTreadmill",
    96: "com.personicle.individual.events.Waterpolo",
    97: "com.personicle.individual.events.Weightlifting",
    116: "com.personicle.individual.events.WalkingStroller",
    98: "com.personicle.individual.events.Wheelchair",
    99: "com.personicle.individual.events.Windsurfing",
    100: "com.personicle.individual.events.Yoga",
    101: "com.personicle.individual.events.Zumba",
}


DATA_DICTIONARY = {
    # Activity data types
    "com.google.calories.bmr": "com.personicle.individual.datastreams.resting_calories",
    "com.google.calories.expended": "com.personicle.individual.datastreams.interval.total_calories",
    "com.google.cycling.pedaling.cadence": "com.personicle.individual.datastreams.cycling.cadence",
    "com.google.cycling.pedaling.cumulative": "com.personicle.individual.datastreams.interval.cycling.cumulative_cadence",
    "com.google.heart_minutes": "com.personicle.individual.datastreams.interval.heart_intensity_minutes",
    "com.google.active_minutes": "com.personicle.individual.datastreams.interval.active_minutes",
    "com.google.power.sample": "com.personicle.individual.datastreams.cycling.power",
    "com.google.step_count.cadence": "com.personicle.individual.datastreams.step.cadence",
    "com.google.step_count.delta": "com.personicle.individual.datastreams.interval.step.count",
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
    "com.google.cycling.wheel_revolution.cumulative": "com.personicle.individual.datastreams.interval.cycling.cumulative_cadence",
    "com.google.distance.delta": "com.personicle.individual.datastreams.interval.distance",
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

########################


DATASTREAM_PARSERMAPPING = {
    # Activity data types
    "com.google.calories.bmr": google_datastream_parser,
    "com.google.calories.expended": google_interval_datastream_parser,
    "com.google.cycling.pedaling.cadence": google_datastream_parser,
    "com.google.cycling.pedaling.cumulative": google_interval_datastream_parser,
    "com.google.heart_minutes": google_interval_datastream_parser,
    "com.google.active_minutes": google_interval_datastream_parser,
    "com.google.power.sample": google_datastream_parser,
    "com.google.step_count.cadence": google_datastream_parser,
    "com.google.step_count.delta": google_interval_datastream_parser,
    "com.google.step_count.cumulative": google_datastream_parser, ##tbd
    # different exercise performed in a workout, should be stored as events in the personicle
    # "com.google.activity.exercise": "personal_events",
    # "com.google.activity.segment": "personal_events",

    # Body data types
    "com.google.body.fat.percentage": google_datastream_parser,
    "com.google.heart_rate.bpm": google_datastream_parser,
    "com.google.height": google_datastream_parser,
    "com.google.weight": google_datastream_parser,

    # Location data types
    "com.google.cycling.wheel_revolution.rpm": google_datastream_parser,
    "com.google.cycling.wheel_revolution.cumulative": google_interval_datastream_parser,
    "com.google.distance.delta": google_interval_datastream_parser,
    # "com.google.location.sample": "location",
    "com.google.speed": google_datastream_parser,

    # Nutrition data types
    # "com.google.hydration": "water_intake",
    # meal event from google fit
    # "com.google.nutrition": "food_event"

    # Sleep data types
    "com.google.sleep.segment": google_datastream_parser, #tbd #write another parser

    #Health data types
    "com.google.blood_glucose": google_datastream_parser,
    # "com.google.blood_pressure": "blood_pressure",
    # "com.google.body.temperature": "body_temperature",
    # "com.google.cervical_mucus": "cervical_mucus",
    # "com.google.cervical_position": "cervical_position",
    # "com.google.menstruation": "menstruation",
    # "com.google.ovulation_test": "ovulation_test",
    # "com.google.oxygen_saturation": "blood_oxygen_saturation",
    # "com.google.vaginal_spotting": "vaginal_spotting"

}