import requests
import sys
import os
import pandas as pd
import traceback
from datetime import datetime


URL = 'https://service.nalog.ru/invalid-inn-proc.json?k=fl&inn'

data = []


def find(inn, retries = 2):
	for i in range(1 + retries):
		try:
			response = requests.get(URL, params={'k': 'fl', 'inn': inn})
			return response.json()
		except Exception:
			print('запрос не работает капец')
			traceback.print_exc()

			if i < retries:
				print('щас пробую снова')
	else:
		return None


def get_output_path():
	with open('./config.txt') as f:
		path = f.readline().strip()
		try:
			os.makedirs(path)
		except FileExistsError:
			pass
		return path


def fixrecord(record) -> dict:
	"""flatten record into a single dict"""
	# todo: check
	return record


def do(df):
	i = 1
	length = df.shape[0]
	for line in df.index:
		row = df.iloc[line]

		inn = row['ИНН']

		datum = find(inn)

		if datum is None:
			continue

		assert 'inn' in datum, 'формат ответа сломался'

		frecord = fixrecord(datum)
		assert isinstance(frecord, dict), 'с сайта вернулось непонятно что'
		data.append(frecord)

		print("{}\t{}%".format(i, (i * 10000 // length) / 100))
		i += 1

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		file_path = sys.argv[1]
	else:
		file_path = input('input file: ')
	print('читаю', file_path)
	try:
		df = pd.read_excel(file_path)
	except Exception as e:
		print('не читается файл')
		traceback.print_exc()
		sys.exit()

	do(df)

	res = pd.DataFrame(data)
	res.to_excel(os.path.join(get_output_path(), f'{datetime.today().strftime("%y%m%d%H%M%S")}.xlsx'), index=False)
