def read_multifasta(file_path):

    is_entry = False
    fasta_dict = {}
    sequence = []
    key = None

    with open(file_path, 'r') as fasta:
        for line in fasta:
            if line[0] == '>':

                if is_entry:
                    fasta_dict[key] = ''.join(sequence)
                    sequence = []

                key = line.split(' ')[0][1:].rstrip()
                is_entry = True

            else:
                if line[0] != '\n':
                    sequence.append(line.rstrip())
    fasta_dict[key] = ''.join(sequence)
    return(fasta_dict)

def run_blast(node_name, contig_dict, E_VALUE_THRESH = 0.04):
    
    from Bio.Blast import NCBIWWW
    
    from Bio.Blast import NCBIXML
    
    node = contig_dict[node_name]
    
    result_handle = NCBIWWW.qblast('blastn', 'nr', node)
    
    blast_record = NCBIXML.read(result_handle)
    
    for alignment in blast_record.alignments:
     for hsp in alignment.hsps:
         if hsp.expect < E_VALUE_THRESH:
             print('****Alignment****')
             print('sequence:', alignment.title)
             print('length:', alignment.length)
             print('e value:', hsp.expect)
             print('Identity: ', hsp.identities)
             print('Gaps: ', hsp.gaps)
             print('Alignment Length: ', hsp.align_length)
             print(hsp.query)
             print(hsp.match)
             print(hsp.sbjct)
             print('\n')


def find_vsgs(contigs_dict):
    import re

    vsgs = {}
    for id in contigs_dict.keys():
        seq = contigs_dict[id]
        pos_fw = seq.find('TGATATATTTTAAC')
        pos_rev = seq.find('GTTAAAATATATCA')

        if pos_fw > -1 or pos_rev > -1:
            print(id)
            vsgs[id] = contigs_dict[id]

    return(vsgs)


def write_fasta(seq_dict, output_file):

    with open(output_file, 'w') as outf:
        for id in seq_dict.keys():
            outf.write('>' + id + '\n')
            outf.write(seq_dict[id] + '\n')


def run_blast_dict(seq_dict):

    import sys
    import os

    os.system('mkdir BLASToutput')
    orig_stdout = sys.stdout

    for id in seq_dict.keys():
        f = open('BLASToutput/' + id + '_BLASTn.txt', 'w')
        sys.stdout = f
        run_blast(id, seq_dict)
        f.close()

    sys.stdout = orig_stdout


if __name__ == '__main__':
    
    import argparse

    parser = argparse.ArgumentParser(description='Find VSGs in your contig assembly')

    parser.add_argument('-i', '--input', 
        help = 'Defines the input multi-fasta file.')

    parser.add_argument('-b', '--blast', action = 'store_true',
        help = 'If flag is given, the programm will blast all found VSG contigs.')

    args = parser.parse_args()
    

    # Run the program
    contigs = read_multifasta(args.input)
    vsgs = find_vsgs(contigs)
    write_fasta(vsgs, 'VSG_contigs.fasta')

    if args.blast:
        print('Running BLASTn, please be patient.\n')
        run_blast_dict(vsgs)
