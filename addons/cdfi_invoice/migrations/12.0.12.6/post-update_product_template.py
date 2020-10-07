def migrate(cr, version):
    # update new description_cve_prod column with the temporary one
    cr.execute("""UPDATE product_template AS pt SET description_cve_prod=ccp.id 
    FROM catalogos_claveprodserv AS ccp 
    WHERE pt.temporary_cve_prod = ccp.c_claveprodserv""")
    # Drop temporary column
    cr.execute('ALTER TABLE product_template DROP COLUMN temporary_cve_prod')

