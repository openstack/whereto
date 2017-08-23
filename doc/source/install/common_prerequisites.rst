Prerequisites
-------------

Before you install and configure the whereto service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``whereto`` database:

     .. code-block:: none

        CREATE DATABASE whereto;

   * Grant proper access to the ``whereto`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON whereto.* TO 'whereto'@'localhost' \
          IDENTIFIED BY 'WHERETO_DBPASS';
        GRANT ALL PRIVILEGES ON whereto.* TO 'whereto'@'%' \
          IDENTIFIED BY 'WHERETO_DBPASS';

     Replace ``WHERETO_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``whereto`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt whereto

   * Add the ``admin`` role to the ``whereto`` user:

     .. code-block:: console

        $ openstack role add --project service --user whereto admin

   * Create the whereto service entities:

     .. code-block:: console

        $ openstack service create --name whereto --description "whereto" whereto

#. Create the whereto service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        whereto public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        whereto internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        whereto admin http://controller:XXXX/vY/%\(tenant_id\)s
