from .base_coordinates import BaseCoordinates

class GeneCoordinates(BaseCoordinates):
    """Handle gene structure and annotation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcript_id = None
        self.gene_annotation = None
        self.exon_height = 20
        self.intron_height = 2

    def set_gene_annotation(self, gtf_file):
        """Set gene annotation from GTF file"""
        self.gene_annotation = self._parse_gtf_file(gtf_file)

    def _parse_gtf_file(self, gtf_file):
        features = []
        with open(gtf_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                fields = line.strip().split('\t')
                if len(fields) < 9:
                    continue
                    
                feature_type = fields[2]
                start = int(fields[3])
                end = int(fields[4])
                strand = fields[6]
                
                attributes = self._parse_attributes(fields[8])
                
                if ('transcript_id' in attributes and attributes['transcript_id'] == self.transcript_id) or \
                   ('Parent' in attributes and attributes['Parent'] == f'transcript:{self.transcript_id}'):
                    
                    if feature_type in ['exon', 'CDS']:
                        features.append({
                            'type': feature_type,
                            'start': start,
                            'end': end,
                            'strand': strand
                        })
        return features

    def _parse_attributes(self, attr_string):
        """Parse attributes string flexibly supporting both GFF and GTF formats"""
        attributes = {}
        
        if '=' in attr_string:  # GFF3 format
            for attr in attr_string.split(';'):
                if not attr.strip():
                    continue
                if '=' in attr:
                    key, value = attr.strip().split('=', 1)
                    attributes[key] = value.strip('"')
        else:  # GTF format
            for attr in attr_string.split(';'):
                if not attr.strip():
                    continue
                try:
                    key, value = [x.strip() for x in attr.strip().split(' ', 1)]
                    attributes[key] = value.strip('"')
                except ValueError:
                    continue
        
        return attributes

    def get_transcript_coordinates(self, gtf_file, transcript_id):
        """Extract transcript coordinates from GFF/GTF file"""
        self.transcript_id = transcript_id
        
        with open(gtf_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                fields = line.strip().split('\t')
                if len(fields) < 9:
                    continue
                
                attributes = self._parse_attributes(fields[8])
                
                found_transcript = False
                if 'transcript_id' in attributes and attributes['transcript_id'] == transcript_id:
                    found_transcript = True
                elif 'ID' in attributes and attributes['ID'] == f'transcript:{transcript_id}':
                    found_transcript = True
                
                if found_transcript:
                    self.chrom = fields[0]
                    self.start_pos = int(fields[3])
                    self.end_pos = int(fields[4])
                    return {
                        'chrom': self.chrom,
                        'start': self.start_pos,
                        'end': self.end_pos
                    }
        
        raise ValueError(f"Transcript {transcript_id} not found in GFF/GTF file") 

    def get_gene_coordinates(self, gtf_file, gene_name):
        """Extract gene coordinates from GTF file
        
        Args:
            gtf_file (str): Path to GTF file
            gene_name (str): Name of the gene to find
            
        Returns:
            dict: Dictionary containing chromosome, start and end positions
            
        Raises:
            ValueError: If gene is not found in GTF file
        """
        from ..parsers.gtf_parser import GTFParser
        parser = GTFParser(debug=self.debug)
        gene_info = parser.parse_gene(gtf_file, gene_name)
        
        # Update instance variables
        self.chrom = gene_info['chrom']
        self.start_pos = gene_info['start']
        self.end_pos = gene_info['end']
        
        return gene_info 