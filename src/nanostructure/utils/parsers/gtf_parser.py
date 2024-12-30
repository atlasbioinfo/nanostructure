import tqdm

class GTFParser:
    """Parse GTF/GFF files"""
    
    def __init__(self, debug=False):
        self.debug = debug

    def _parse_attributes(self, attr_string):
        """Parse attributes string flexibly supporting both GFF and GTF formats"""
        attributes = {}
        
        # Handle GFF3 format (key=value;)
        if '=' in attr_string:
            for attr in attr_string.split(';'):
                if not attr.strip():
                    continue
                if '=' in attr:
                    key, value = attr.strip().split('=', 1)
                    attributes[key] = value.strip('"')
        
        # Handle GTF format (key "value";)
        else:
            for attr in attr_string.split(';'):
                if not attr.strip():
                    continue
                try:
                    key, value = [x.strip() for x in attr.strip().split(' ', 1)]
                    attributes[key] = value.strip('"')
                except ValueError:
                    continue
        
        return attributes

    def parse_gene(self, gtf_file, gene_name):
        """Extract gene coordinates from GTF file"""
        with open(gtf_file) as f:
            for line in tqdm.tqdm(f, desc="Parsing GTF file"):
                if line.startswith('#'):
                    continue
                fields = line.strip().split('\t')
                if len(fields) < 9:
                    continue
                
                attributes = self._parse_attributes(fields[8])
                
                if fields[2] == 'gene' and ('gene_id' in attributes and attributes['gene_id'] == gene_name):
                    return {
                        'chrom': fields[0],
                        'start': int(fields[3]),
                        'end': int(fields[4])
                    }
        
        raise ValueError(f"Gene {gene_name} not found in GTF file")

    def parse_transcript(self, gtf_file, transcript_id):
        """Extract transcript coordinates and features from GFF/GTF file"""
        if self.debug:
            print(f"\nLooking for transcript: {transcript_id}")
        
        features = []
        transcript_info = None
        
        with open(gtf_file) as f:
            for line in tqdm.tqdm(f, desc="Parsing GTF file"):
                if line.startswith('#'):
                    continue
                fields = line.strip().split('\t')
                if len(fields) < 9:
                    continue
                
                attributes = self._parse_attributes(fields[8])
                
                # Check various possible transcript identifiers
                found_transcript = False
                if 'transcript_id' in attributes and attributes['transcript_id'] == transcript_id:
                    found_transcript = True
                elif 'ID' in attributes and attributes['ID'] == f'transcript:{transcript_id}':
                    found_transcript = True
                
                if found_transcript:
                    if not transcript_info:
                        transcript_info = {
                            'chrom': fields[0],
                            'start': int(fields[3]),
                            'end': int(fields[4])
                        }
                    
                    if fields[2] in ['exon', 'CDS']:
                        features.append({
                            'type': fields[2],
                            'start': int(fields[3]),
                            'end': int(fields[4]),
                            'strand': fields[6]
                        })
                        if self.debug:
                            print(f"Found {fields[2]}: {fields[3]}-{fields[4]} ({fields[6]})")
        
        if not transcript_info:
            raise ValueError(f"Transcript {transcript_id} not found in GFF/GTF file")
            
        transcript_info['features'] = features
        return transcript_info 