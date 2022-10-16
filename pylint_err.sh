# pip3 install pylint
Ignore="C0103|C0114|C0115|C0116|C0209|C0325|C0301|R0903|R0914"
pylint --recursive=y ./src | egrep -v $Ignore > pylint_err.txt