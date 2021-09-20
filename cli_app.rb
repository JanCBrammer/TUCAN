# (c) CC BY-SA | Jan C. Brammer, RWTH Aachen and Ulrich Schatzschneider, Universität Würzburg | NFDI4Chem | v2.1 | 18.09.2021

require './inchi'
require 'optparse'

# run as `ruby cli_app.rb --molfile=<path/to/molefile>`
# run with `--permute-input` flag in order to randomly permute the atom indices

class CommandLineInterface
  include Inchi

  def initialize
    options = {}
    begin
    OptionParser.new do |opts|
      opts.on('--molfile MOLFILE') { |o| options[:molfile] = o }
      opts.on('--permute-input') { |o| options[:permute] = o }
      opts.on('--dot-file') { |o| options[:dot_file] = o }
    end.parse!
    rescue OptionParser::InvalidOption => e
      abort("#{e}")
    end

    @filename = options[:molfile]
    abort('Please provide a filename.') if @filename.nil?
    abort("File `#{@filename}` doesn't exist.") unless File.exist?(@filename)
    @permute = options[:permute] || false
    @print_dot_file = options[:dot_file] || false
  end

  def run
    puts "#{'-' * 100}\n"
    puts "\nA new International Chemical Identifier (nInChI) v2.1\n"
    puts "\nJan Brammer (RWTH Aachen) and Ulrich Schatzschneider (Universität Würzburg) within NFDI4Chem\n"
    puts "\nCC BY-SA 09/2021\n"
    puts "\n#{'-' * 100}\n"
    molfile_data = read_molfile(@filename)
    puts "\nPrinting molfile: #{@filename}. First 4 lines contain header."
    puts "\n#{'-' * 75}\n"
    molfile_data.each { |line| puts line }
    puts "\n#{'-' * 75}\n"
    molecule = create_molecule_array(molfile_data, PeriodicTable::ELEMENTS)
    adjacency_matrix, atom_list = create_adjacency_matrix(molecule)
    adjacency_matrix, atom_list = sort_adjacency_matrix(adjacency_matrix, atom_list)
    print "\nFINAL STAGE \n"
    print_adjacency_matrix(adjacency_matrix, atom_list)
    puts "\n#{write_ninchi_string(molecule,adjacency_matrix, PeriodicTable::ELEMENTS)}"
    puts "\n#{write_dot_file(adjacency_matrix, atom_list, @filename, PeriodicTable::ELEMENTS, PeriodicTable::ELEMENT_COLORS)}" if @print_dot_file
    puts "\nOutput format: DOT file - to display go to https://dreampuf.github.io/GraphvizOnline/#" if @print_dot_file
    puts "\n#{'-' * 100}\n"
  end
end

CommandLineInterface.new.run
