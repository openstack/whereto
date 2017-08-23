2. Edit the ``/etc/whereto/whereto.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://whereto:WHERETO_DBPASS@controller/whereto
