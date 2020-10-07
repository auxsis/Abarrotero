def migrate(cr, version):
    cr.execute('ALTER TABLE product_template ADD temporary_cve_prod varchar')
    cr.execute('UPDATE product_template SET temporary_cve_prod=clave_producto WHERE true')
    


