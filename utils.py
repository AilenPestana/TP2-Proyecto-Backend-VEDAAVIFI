def paginar(request, total):

    limit = request.args.get('_limit', 10, type=int)
    offset = request.args.get('_offset', 0, type=int)


# Evito errores, el limite es la cantidad d pags q vemos, no puede ser menor o 0.
    if limit <= 0:
        limit = 10
#offset es la cantidad de página que se omiten, no pueden ser menor a 0.
    if offset < 0:
        offset = 0

#Buscamos la ultima pag, total son todas las pags
    if total > 0:
        ult_offset = ((total - 1)//limit)*limit
    else:
        ult_offset = 0
    
#Ruta del endpoint
    base = request.base_url

    filtros = ""
    #Guardo filtros como equipo, fecha, fase, ignorando limit y offset
    for parametro, valor in request.args.items():
        if parametro != '_limit' and parametro != '_offset':
            if filtros != "":
                filtros += "&"
            filtros += str(parametro) + "=" + str(valor)
    
    #Funcion para armar las url, recibe un numero como offset
    def armar_url(offs):
        url = base + "?" 
        if filtros != "":
            url = url + filtros + "&"
    
        url = url + "_limit=" + str(limit)
        url = url + "&_offset=" + str(offs)
    
        return url
    
       
    links = {}#links para paginas
    
    # primera
    links["_first"] = armar_url(0)
    
    # anterior
    if offset > 0:
        prev_offset = offset - limit
        if prev_offset < 0:
            prev_offset = 0
        links["_prev"] = armar_url(prev_offset)
    else:
        links["_prev"] = None
    
    # siguiente
    if offset + limit < total:
        links["_next"] = armar_url(offset + limit)
    else:
        links["_next"] = None
    
    # última
    links["_last"] = armar_url(ult_offset)
    
    return links, limit, offset
    
    