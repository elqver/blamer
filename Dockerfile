FROM blamer_python_deps
COPY app /app/
WORKDIR app

CMD sh -c "python -m alembic upgrade head && python main.py"

