import argparse
from datetime import datetime


def get_params():

	parser = argparse.ArgumentParser()

	parser.add_argument(
		'url',
		help='URL for public github repository\nhttps://github.com/username/repository'
	)
	parser.add_argument(
		'-s',
		'--start_date',
		default=None,
		type=datetime.fromisoformat,
		required=False,
		help='Start date value of period for data analysis',
	)
	parser.add_argument(
		'-e',
		'--end_date',
		default=datetime.now(),
		type=datetime.fromisoformat,
		required=False,
		help='End date value of period for data analysis'
	)
	parser.add_argument(
		'-b',
		'--branch',
		default='master',
		type=str,
		required=False,
		help='branch'
	)
	args = vars(parser.parse_args())
	return args
