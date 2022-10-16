# pip3 install pylint

File="pylint_err.log"
Ignore="C0103|C0114|C0115|C0116|C0209|C0325|C0301|R0903|R0914"

echo "Creating $File ..."
pylint --recursive=y ./src | egrep -v $Ignore > $File
