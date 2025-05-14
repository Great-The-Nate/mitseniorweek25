import os

round_one_folder = 'round_one'
with open('degree_lists/class_of_2025.txt') as f:
	class_of_2025_emails = set(line.strip().lower() for line in f)
with open('degree_lists/all_degrees2025.txt') as f:
	all_degrees2025_emails = set(line.strip().lower() for line in f)

emails = set()
for filename in os.listdir(round_one_folder):
	if filename.startswith('accepted_'):
		with open(os.path.join(round_one_folder, filename)) as f:
			for line in f:
				if line.strip() == '':
					break
				# email = line.strip().split(',')[1][2:-1] + "@mit.edu" # for wagers files
				email = line.strip() # for accepted files
				if email.lower() not in class_of_2025_emails and email.lower() not in all_degrees2025_emails:
					print('%s: %s not found in class_of_2025.txt or all_degrees2025.txt' % (filename, email))
					emails.add(email)
                
print('Flagged emails: %s' % str(list(emails)))
