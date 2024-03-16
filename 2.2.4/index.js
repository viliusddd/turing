/**
 * Create square grid for tic tac toe game.
 * @param {number} gridColumns - expects 9 or 16
 * @return {void}
 */
function createGrid(gridColumns=3) {
  const doc = document
  const grid = doc.createElement('div')
  grid.setAttribute('id', 'grid')
  doc.body.appendChild(grid)

  grid.style.gridTemplateColumns = `repeat(${gridColumns}, 1fr)`

  const arrOfNums = Array
      .from({length: gridColumns * gridColumns}, (_, k) => k + 1)
  console.log(arrOfNums)

  /** @type {{string: number}} */
  // const squares = {}

  for (const num of arrOfNums) {
    const square = doc.createElement('div')
    square.setAttribute('id', `sqr-${num}`)
    square.setAttribute('class', 'notselected')
    square.tabIndex = `${num}`
    squares[square.id] = undefined

    square.addEventListener('click', function() {
      square.removeAttribute('notselected')
      square.setAttribute('class', 'selected')
      squares[square.id] = 1
    }, {once: true})

    grid.appendChild(square)
  }
  console.log(squares)
}

function createResetBtn() {
  const doc = document
  const btn = doc.createElement('button')
  btn.setAttribute('id', 'reset')
  btn.textContent = 'Reset'

  doc.body.appendChild(btn)
}

function getUndefinedSquares() {
  const convSquares = Object.entries(squares)

  const filteredSquares = convSquares
      .filter(([_, val]) => val === undefined)

  return Object.fromEntries(filteredSquares)
}

function aiMove(moves) {
  const randIndex = Math.floor(Math.random() * Object.keys(moves).length)
  return Object.keys(moves)[randIndex]
}

class Player {
  constructor(name, icon) {
    this.name = name
    this.icon = icon
    this.score = 0
  }
}


const player1 = new Player('Vilius', 'x')
const player2 = new Player('PC', 'circle')

const squares = {}

while (true) {
  createGrid(3)
  // aiMove(getUndefinedSquares())


}
