from pizzeria import pizzeria
from flask import render_template, request, redirect, url_for, flash, session
from models import db, Cliente, Pizza, Pedido, DetallePedido
import forms
import datetime

@pizzeria.route("/orden", methods=["GET"])
def index():
    items = session.get('carrito', [])
    subtotal = sum(p['subtotal'] for p in items)
    comprador = session.get('comprador', {})
    return render_template("pizzeria/index.html",
        items=items,
        subtotal=subtotal,
        comprador=comprador
    )

@pizzeria.route("/orden/nueva", methods=["GET", "POST"])
def agregar():
    form_cliente = forms.ClienteForm(request.form)
    form_pizza = forms.PizzaForm(request.form)

    if request.method == "GET":
        comprador = session.get('comprador', {})
        if comprador:
            form_cliente.nombre.data = comprador.get('nombre')
            form_cliente.direccion.data = comprador.get('direccion')
            form_cliente.telefono.data = comprador.get('telefono')
            if comprador.get('fecha'):
                form_cliente.fecha.data = datetime.datetime.strptime(
                    comprador.get('fecha'), '%d-%m-%Y').date()

    if request.method == "POST":
        if form_cliente.validate() and form_pizza.validate():
            session['comprador'] = {
                'nombre': form_cliente.nombre.data,
                'direccion': form_cliente.direccion.data,
                'telefono': form_cliente.telefono.data,
                'fecha': form_cliente.fecha.data.strftime('%d-%m-%Y')
            }

            tamano = form_pizza.tamano.data
            cantidad = form_pizza.num_pizzas.data

            extras = []
            if form_pizza.jamon.data:
                extras.append("Jamón")
            if form_pizza.pina.data:
                extras.append("Piña")
            if form_pizza.champinones.data:
                extras.append("Champiñones")

            extras_str = ", ".join(extras) if extras else "Sin extras"

            precios = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
            base = precios[tamano]
            subtotal = (base + len(extras) * 10) * cantidad

            carrito = session.get('carrito', [])
            carrito.append({
                'tamano': tamano,
                'extras': extras_str,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            session['carrito'] = carrito
            flash("¡Pizza agregada al pedido!", "success")
            return redirect(url_for('pizzeria.index'))
        else:
            flash("Revisa los campos e intenta de nuevo.", "error")

    return render_template("pizzeria/agregar.html",
        form_cliente=form_cliente,
        form_pizza=form_pizza
    )

@pizzeria.route("/orden/eliminar/<int:pos>", methods=["GET", "POST"])
def quitar(pos):
    carrito = session.get('carrito', [])

    if pos < 0 or pos >= len(carrito):
        flash("El elemento no existe en el pedido.", "error")
        return redirect(url_for('pizzeria.index'))

    item = carrito[pos]

    if request.method == "POST":
        carrito.pop(pos)
        session['carrito'] = carrito
        flash("Pizza eliminada del pedido.", "success")
        return redirect(url_for('pizzeria.index'))

    return render_template("pizzeria/quitar.html", item=item, pos=pos)

@pizzeria.route("/orden/confirmar", methods=["POST"])
def terminar():
    carrito = session.get('carrito', [])
    comprador = session.get('comprador', {})

    if not carrito:
        flash("Tu pedido está vacío. Agrega al menos una pizza.", "error")
        return redirect(url_for('pizzeria.index'))

    if not comprador:
        flash("Faltan los datos del cliente.", "error")
        return redirect(url_for('pizzeria.index'))

    total = sum(p['subtotal'] for p in carrito)

    cliente = Cliente(
        nombre=comprador['nombre'],
        direccion=comprador['direccion'],
        telefono=comprador['telefono']
    )
    db.session.add(cliente)
    db.session.flush()

    fecha = datetime.datetime.strptime(comprador['fecha'], '%d-%m-%Y').date()

    pedido = Pedido(
        id_cliente=cliente.id_cliente,
        fecha=fecha,
        total=total
    )
    db.session.add(pedido)
    db.session.flush()

    for p in carrito:
        pizza = Pizza(
            tamano=p['tamano'],
            ingredientes=p['extras'],
            precio=p['subtotal'] / p['cantidad']
        )
        db.session.add(pizza)
        db.session.flush()

        detalle = DetallePedido(
            id_pedido=pedido.id_pedido,
            id_pizza=pizza.id_pizza,
            cantidad=p['cantidad'],
            subtotal=p['subtotal']
        )
        db.session.add(detalle)

    db.session.commit()
    session.pop('carrito', None)
    session.pop('comprador', None)

    flash(f"¡Pedido confirmado! Total a pagar: ${total}", "success")
    return redirect(url_for('pizzeria.index'))

@pizzeria.route("/reportes", methods=["GET", "POST"])
def consultas():
    registros = []
    total_acumulado = 0
    tipo = None
    busqueda = None
    detalle_pedido = None

    if request.method == "POST" and 'buscar' in request.form:
        tipo = request.form.get('tipo')
        busqueda = request.form.get('busqueda', '').strip().lower()

        dias = {
            'lunes': 0, 'martes': 1, 'miércoles': 2, 'miercoles': 2,
            'jueves': 3, 'viernes': 4, 'sabado': 5, 'domingo': 6
        }
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        if tipo == 'dia':
            num_dia = dias.get(busqueda)
            if num_dia is None:
                flash("Día inválido. Escribe: lunes, martes, miércoles...", "error")
            else:
                todos = Pedido.query.join(Cliente).all()
                registros = [p for p in todos if p.fecha.weekday() == num_dia]
                total_acumulado = sum(float(p.total) for p in registros)
                if not registros:
                    flash(f"Sin ventas registradas el día {busqueda}.", "error")

        elif tipo == 'mes':
            num_mes = meses.get(busqueda)
            if num_mes is None:
                flash("Mes inválido. Escribe: enero, febrero, marzo...", "error")
            else:
                todos = Pedido.query.join(Cliente).all()
                registros = [p for p in todos if p.fecha.month == num_mes]
                total_acumulado = sum(float(p.total) for p in registros)
                if not registros:
                    flash(f"Sin ventas registradas en {busqueda}.", "error")

    if request.method == "POST" and 'ver_detalle' in request.form:
        id_pedido = request.form.get('id_pedido')
        detalle_pedido = db.session.get(Pedido, int(id_pedido))
        tipo = request.form.get('tipo')
        busqueda = request.form.get('busqueda')

    return render_template("pizzeria/consultas.html",
        registros=registros,
        total_acumulado=total_acumulado,
        tipo=tipo,
        busqueda=busqueda,
        detalle_pedido=detalle_pedido
    )