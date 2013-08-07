/**
 *  Copyright 2007-2008 University Of Southern California
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing,
 *  software distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
package edu.isi.pegasus.planner.transfer.mapper.impl;

import edu.isi.pegasus.common.logging.LogManager;

import edu.isi.pegasus.planner.classes.ADag;
import edu.isi.pegasus.planner.classes.PegasusBag;
import edu.isi.pegasus.planner.classes.PlannerOptions;

import edu.isi.pegasus.planner.transfer.mapper.MapperException;

import java.io.IOException;

import org.griphyn.vdl.euryale.FileFactory;
import org.griphyn.vdl.euryale.VirtualFlatFileFactory;

/**
 * Maps the output files to a flat directory on the output site.
 * 
 * @author Karan Vahi
 */
public class Flat extends AbstractFileFactoryBasedMapper {

    /**
     * The short name for the mapper
     */
    public static final String SHORT_NAME = "Flat";

    /**
     * The default constructor.
     */
    public Flat(){
        
    }
    
    /**
     * Initializes the mappers.
     *
     * @param bag   the bag of objects that is useful for initialization.
     * @param workflow   the workflow refined so far.
     *
     */
    public void initialize( PegasusBag bag, ADag workflow)  throws MapperException{
        super.initialize(bag, workflow);
    }
    
   
    /**
     * Instantiates a Flat File Factory and returns it.
     * 
     * @param bag   the bag of objects that is useful for initialization.
     * @param workflow   the workflow refined so far.
     * 
     * @return the handle to the File Factory to use 
     */
    public  FileFactory instantiateFileFactory( PegasusBag bag, ADag workflow ){
        String addOn = mSiteStore.getRelativeStorageDirectoryAddon( );
        FileFactory factory;
        
        //all file factories intialized with the addon component only
        try {
            //Create a flat file factory
            factory = new VirtualFlatFileFactory( addOn ); // minimum default
        } catch ( IOException ioe ) {
            throw new MapperException( this.getErrorMessagePrefix() + "Unable to intialize the Flat File Factor " ,
                                            ioe );
        }
        return factory;
    }
    
    /**
     * Returns the short name for the implementation class.
     * 
     * @return 
     */
    public  String getShortName(){
        return Flat.SHORT_NAME;
    }
   
}
