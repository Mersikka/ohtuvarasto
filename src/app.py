from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto


app = Flask(__name__)


class WarehouseStorage:
    def __init__(self):
        self.warehouses = {}
        self.id_counter = 0

    def get_next_id(self):
        self.id_counter += 1
        return self.id_counter

    def clear(self):
        self.warehouses.clear()
        self.id_counter = 0


storage = WarehouseStorage()
warehouses = storage.warehouses


@app.route('/')
def index():
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            tilavuus = float(request.form.get('tilavuus', 0))
            alku_saldo = float(request.form.get('alku_saldo', 0))
        except ValueError:
            return render_template(
                'create_warehouse.html',
                error='Invalid values'
            )

        if not name:
            return render_template(
                'create_warehouse.html',
                error='Name required'
            )

        warehouse_id = storage.get_next_id()
        warehouses[warehouse_id] = {
            'name': name,
            'varasto': Varasto(tilavuus, alku_saldo)
        }
        return redirect(url_for('index'))

    return render_template('create_warehouse.html')


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))
    return render_template(
        'view_warehouse.html',
        warehouse_id=warehouse_id,
        warehouse=warehouse
    )


def handle_edit_post(warehouse_id, warehouse):
    name = request.form.get('name', '').strip()
    try:
        tilavuus = float(request.form.get('tilavuus', 0))
    except ValueError:
        return render_template(
            'edit_warehouse.html',
            warehouse_id=warehouse_id,
            warehouse=warehouse,
            error='Invalid capacity'
        )

    if not name:
        return render_template(
            'edit_warehouse.html',
            warehouse_id=warehouse_id,
            warehouse=warehouse,
            error='Name required'
        )

    warehouse['name'] = name
    warehouse['varasto'] = Varasto(tilavuus, warehouse['varasto'].saldo)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    if request.method == 'POST':
        return handle_edit_post(warehouse_id, warehouse)

    return render_template(
        'edit_warehouse.html',
        warehouse_id=warehouse_id,
        warehouse=warehouse
    )


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_to_warehouse(warehouse_id):
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    try:
        maara = float(request.form.get('maara', 0))
    except ValueError:
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse['varasto'].lisaa_varastoon(maara)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_from_warehouse(warehouse_id):
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    try:
        maara = float(request.form.get('maara', 0))
    except ValueError:
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse['varasto'].ota_varastosta(maara)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    if warehouse_id in warehouses:
        del warehouses[warehouse_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
