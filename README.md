# mediatory-backend


## Install project on your local


```
cd existing_repo
git remote add origin http://www.gitlab.local/genus/mediatory-backend.git
git branch -M main
git push -uf origin main
```

## install Python and make virtual environment
Check your python version recomandation version is 3.8.12

``` python -V ```

And install dependency with requirements.txt

```shell
python -m venv venv/path
cd venv/path/Script/activate
python -m pip install -r requirements.txt
```

## Start server with development environment.

```shell
python manage.py runserver 0.0.0.0.:{port}
```

## 
