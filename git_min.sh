clear

Name="py-vRelaySrv"
Dir="src"
Repo="https://github.com/VladVons/$Name"
echo "Repo: $Repo"

rm -Rf $Name

CloneC()
{
    git clone --no-checkout $Repo
    cd $Name
    git sparse-checkout init --cone
    git sparse-checkout set $Dir
}

CloneC
