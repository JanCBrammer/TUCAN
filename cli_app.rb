require './inchi'
require 'optparse'
require './periodic_table'

# run as `ruby cli_app.rb --molfile=<path/to/molefile>`
# run with `--permute-input` flag in order to randomly permute the atom indices

class CommandLineInterface
  include Inchi
  include PeriodicTable

  def initialize
    options = {}
    OptionParser.new do |opt|
      opt.on('--molfile MOLFILE') { |o| options[:molfile] = o }
      opt.on('--permute-input') { |o| options[:permute] = o }
    end.parse!
    @filename = options[:molfile]
    @permute = options[:permute] || false
  end

  def run
    puts "\nA new International Chemical Identifier (nInChI)"
    puts 'CC BY-SA | Ulrich Schatzschneider | Universität Würzburg | NFDI4Chem | v1.4 | 06/2021'

    molfile_data = read_molfile(@filename)
    puts "\nPrinting molfile: #{@filename}. First 4 lines contain header."
    molfile_data.each { |line| puts line }

    molecule = create_molecule_array(molfile_data, PeriodicTable::ELEMENTS)
    molecule = update_molecule_indices(molecule, random_indices: true) if @permute
    canonicalized_molecule = canonicalize_molecule(molecule)
    puts "\n#{write_ninchi_string(canonicalized_molecule, PeriodicTable::ELEMENTS)}"
    puts "\n#{write_dot_file(canonicalized_molecule, PeriodicTable::ELEMENTS, PeriodicTable::ELEMENT_COLORS)}"
    puts 'Output format: DOT file - to display go to https://dreampuf.github.io/GraphvizOnline/#'
  end
end

CommandLineInterface.new.run
