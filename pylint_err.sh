# pip3 install pylint

File="pylint_err.log"

#Ignore="C0103|C0114|C0115|C0116|C0209|C0325|C0301|R0903|R0914"

Ignore="invalid-name|\
missing-function-docstring|\
missing-module-docstring|\
missing-class-docstring|\
too-few-public-methods|\
too-many-locals|\
line-too-long|\
superfluous-parens|\
consider-using-f-string"

echo "Creating $File ..."
#time pylint --recursive=y ./src > $File
time pylint --recursive=y ./src | egrep -v $Ignore > $File
