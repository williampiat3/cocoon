try:
	with open ('count.txt','r') as counting:
		content=int(counting.read())
except IOError:
	with open ('count.txt','w') as counting:
		counting.write("0")
	with open ('count.txt','r') as counting:
		content=int(counting.read())

with open ('count.txt','w') as counting:
	counting.write(str(content+1))