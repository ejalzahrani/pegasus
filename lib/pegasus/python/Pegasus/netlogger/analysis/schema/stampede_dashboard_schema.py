"""
Contains the code to create and map objects to the Stampede DB schema
via a SQLAlchemy interface.
"""
__author__ = "Monte Goode"
__author__ = "Karan Vahi"

import time
import warnings
import logging

from sqlalchemy import *
from sqlalchemy import orm, exc

from Pegasus.netlogger.analysis.schema._base import SABase

log = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 4.0

# Empty classes that will be populated and mapped
# to tables via the SQLAlch mapper.
class DashboardWorkflow(SABase):
    pass

class DashboardWorkflowstate(SABase):
    pass

from Pegasus.service.catalogs import ReplicaCatalog, RC_FORMATS
from Pegasus.service.catalogs import SiteCatalog, SC_FORMATS
from Pegasus.service.catalogs import TransformationCatalog, TC_FORMATS
from Pegasus.service.ensembles import Ensemble, EnsembleStates
from Pegasus.service.ensembles import EnsembleWorkflow, EnsembleWorkflowStates

def initializeToDashboardDB(db, metadata, kw={}):
    """
    Function to create the Workflow schema that just tracks the root
    level workflows, if it does not exist,
    if it does exist, then connect and set up object mappings.

    @type   db: SQLAlch db/engine object.
    @param  db: Engine object to initialize.
    @type   metadata: SQLAlch metadata object.
    @param  metadata: Associated metadata object to initialize.
    @type   kw: dict
    @param  kw: Keywords to pass to Table() functions
    """
    KeyInt = Integer
    # MySQL likes using BIGINT for PKs but some other
    # DB don't like it so swap as needed.
    if db.name == 'mysql':
        KeyInt = BigInteger
        kw['mysql_charset'] = 'latin1'

    if db.name == 'sqlite':
        warnings.filterwarnings('ignore', '.*does \*not\* support Decimal*.')


    # pg_workflow definition
    # ==> Information comes from braindump.txt file

    # wf_uuid = autogenerated by database                   wfuuid, submitted, directory, database connection
    # dax_label = label
    # timestamp = pegasus_wf_time
    # submit_hostname = (currently missing)
    # submit_dir = run
    #

    pg_workflow = Table('master_workflow', metadata,
                        Column('wf_id', KeyInt, primary_key=True, nullable=False),
                        Column('wf_uuid', VARCHAR(255), nullable=False),
                        Column('dax_label', VARCHAR(255), nullable=True),
                        Column('dax_version', VARCHAR(255), nullable=True),
                        Column('dax_file', VARCHAR(255), nullable=True),
                        Column('dag_file_name', VARCHAR(255), nullable=True),
                        Column('timestamp', NUMERIC(precision=16,scale=6), nullable=True),
                        Column('submit_hostname', VARCHAR(255), nullable=True),
                        Column('submit_dir', TEXT, nullable=True),
                        Column('planner_arguments', TEXT, nullable=True),
                        Column('user', VARCHAR(255), nullable=True),
                        Column('grid_dn', VARCHAR(255), nullable=True),
                        Column('planner_version', VARCHAR(255), nullable=True),
                        Column('db_url', TEXT, nullable=True),
                        **kw
    )

    Index('KEY_MASTER_WF_ID', pg_workflow.c.wf_id, unique=True)
    Index('UNIQUE_MASTER_WF_UUID', pg_workflow.c.wf_uuid, unique=True)

    try:
        orm.mapper(DashboardWorkflow, pg_workflow )
    except exc.ArgumentError, e:
        log.warning(e)

    pg_workflowstate = Table('master_workflowstate', metadata,
    # All three columns are marked as primary key to produce the desired
    # effect - ie: it is the combo of the three columns that make a row
    # unique.
                             Column('wf_id', KeyInt, ForeignKey('master_workflow.wf_id', ondelete='CASCADE'), 
                                    nullable=False, primary_key=True),
                             Column('state', Enum('WORKFLOW_STARTED', 'WORKFLOW_TERMINATED'), 
                                nullable=False, primary_key=True),
                             Column('timestamp', NUMERIC(precision=16,scale=6), nullable=False, primary_key=True,
                                    default=time.time()),
                             Column('restart_count', INT, nullable=False),
                             Column('status', INT, nullable=True),
                             **kw
    )

    Index('UNIQUE_MASTER_WORKFLOWSTATE',
          pg_workflowstate.c.wf_id,
          pg_workflowstate.c.state,
          pg_workflowstate.c.timestamp, unique=True)

    try:
        orm.mapper(DashboardWorkflowstate, pg_workflowstate)
    except exc.ArgumentError, e:
        log.warning(e)

    pg_replica_catalog = Table("replica_catalog", metadata, 
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('format', Enum(*RC_FORMATS), nullable=False),
        Column('created', DateTime, nullable=False),
        Column('updated', DateTime, nullable=False),
        Column('username', String(100), nullable=False),
        mysql_engine = 'InnoDB',
        **kw
    )

    Index('UNIQUE_REPLICA_CATALOG',
          pg_replica_catalog.c.username,
          pg_replica_catalog.c.name)

    try:
        orm.mapper(ReplicaCatalog, pg_replica_catalog)
    except exc.ArgumentError, e:
        log.warning(e)

    pg_site_catalog = Table('site_catalog', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('format', Enum(*SC_FORMATS), nullable=False),
        Column('created', DateTime, nullable=False),
        Column('updated', DateTime, nullable=False),
        Column('username', String(100), nullable=False),
        mysql_engine = 'InnoDB',
        **kw
    )

    Index('UNIQUE_SITE_CATALOG',
          pg_site_catalog.c.username,
          pg_site_catalog.c.name)

    try:
        orm.mapper(SiteCatalog, pg_site_catalog)
    except exc.ArgumentError, e:
        log.warning(e)

    pg_transformation_catalog = Table('transformation_catalog', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('format', Enum(*TC_FORMATS), nullable=False),
        Column('created', DateTime, nullable=False),
        Column('updated', DateTime, nullable=False),
        Column('username', String(100), nullable=False),
        mysql_engine = 'InnoDB',
        **kw
    )

    Index('UNIQUE_TRANSFORMATION_CATALOG',
          pg_transformation_catalog.c.username,
          pg_transformation_catalog.c.name)

    try:
        orm.mapper(TransformationCatalog, pg_transformation_catalog)
    except exc.ArgumentError, e:
        log.warning(e)

    pg_ensemble = Table('ensemble', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('created', DateTime, nullable=False),
        Column('updated', DateTime, nullable=False),
        Column('state', Enum(*EnsembleStates), nullable=False),
        Column('max_running', Integer, nullable=False),
        Column('max_planning', Integer, nullable=False),
        Column('username', String(100), nullable=False),
        mysql_engine = 'InnoDB'
    )

    Index('UNIQUE_ENSEMBLE',
          pg_ensemble.c.username,
          pg_ensemble.c.name)

    try:
        orm.mapper(Ensemble, pg_ensemble)
    except exc.ArgumentError, e:
        log.warning(e)

    pg_ensemble_workflow = Table('ensemble_workflow', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('created', DateTime, nullable=False),
        Column('updated', DateTime, nullable=False),
        Column('state', Enum(*EnsembleWorkflowStates), nullable=False),
        Column('priority', Integer, nullable=False),
        Column('wf_uuid', String(36)),
        Column('submitdir', String(512)),
        Column('ensemble_id', Integer, ForeignKey('ensemble.id'), nullable=False),
        mysql_engine = 'InnoDB'
    )

    Index('UNIQUE_ENSEMBLE_WORKFLOW',
          pg_ensemble_workflow.c.ensemble_id,
          pg_ensemble_workflow.c.name)

    try:
        orm.mapper(EnsembleWorkflow, pg_ensemble_workflow)
    except exc.ArgumentError, e:
        log.warning(e)

    metadata.create_all(db)

