class BoardDef(object):
    def __init__(self, name):
        self.name = name
        self.sockets = {}
        self.routers = {}
        self.pins = {}
        self.jtag_entry = None

        self.sockets[None] = (-1, {})

    def _setPin(self, name, pin):
        assert name not in self.pins, (self.name, name)
        self.pins[name] = pin

    def addJtagEntry(self, args, opts):
        assert not args
        jtag = int(opts.pop('jtag'))
        assert jtag > 0

        assert not self.jtag_entry
        self.jtag_entry = (jtag,)

    def addSocket(self, args, opts):
        jtag = int(opts.pop('jtag'))
        assert jtag > 0
        assert not opts, opts

        name, = args
        self.sockets[name] = (jtag, {})

    def addRouter(self, args, opts):
        jtag = int(opts.pop('jtag'))
        assert jtag > 0
        part = opts.pop('part')
        assert not opts, opts

        name, = args
        self.routers[name] = (jtag, part, {})

    def addPin(self, args, opts):
        fullname, = args
        socket = None

        name = fullname
        if '.' in fullname:
            socket, name = fullname.split('.')

        p = (socket, name, opts)
        self._setPin(fullname, p)
        if "alias" in opts:
            self._setPin(opts['alias'], p)

        if "port" in opts:
            router_name, router_pin = opts['port'].split('.')
            router = self.routers[router_name]
            assert router_pin not in router[2]
            router[2][router_pin] = (socket, name)

        assert socket in self.sockets
        pins = self.sockets[socket][1]
        assert name not in pins
        pins[name] = p

class Assembly(object):
    def __init__(self, name):
        self.name = name

        self.boards = {}
        self.assignments = []
        self.connections = {}

    def addBoard(self, board_defs, args, opts):
        assert not opts
        boardname, id, connection = args
        assert id not in self.boards
        b = board_defs[boardname]

        d = self.connections.setdefault(id, {})
        if connection != "unconnected":
            if '.' in connection:
                conn_id, conn_socket = connection.split('.')
            else:
                conn_id, conn_socket = connection, None
            assert conn_id in self.boards
            conn_b = self.boards[conn_id][0]
            assert conn_socket in conn_b.sockets
            assert conn_socket not in self.connections[conn_id], (boardname, conn_id, conn_socket)

            d[None] = (conn_id, conn_socket)
            self.connections[conn_id][conn_socket] = (id, None)
        self.boards[id] = (b,)

    def addAssignment(self, args, opts):
        assert opts.pop('') == ''
        assert not opts
        val = ' '.join(args[1:])

        target = args[0]
        board_id, name = target.split('.', 1)
        assert board_id in self.boards

        assert not [1 for (t, s) in self.assignments if t == target]
        self.assignments.append((target, val))

    # def getPinAttrs(self, (boardname, socket, pinname)):
        # boarddef = self.boards[boardname][0]
        # pin_attrs = boarddef.sockets[socket][1][pinname][2]
        # return pin_attrs

    def getRouter(self, pin):
        assert isinstance(pin, AssemblyPin)
        boarddef = self.boards[pin.boardname][0]
        pin_attrs = boarddef.sockets[pin.socket][1][pin.pinname][2]

        if 'port' not in pin_attrs:
            return None

        router_name, router_pin = pin_attrs['port'].split('.')
        router = boarddef.routers[router_name]
        return router

class AssemblyPin(object):
    def __init__(self, boardname, socket, pinname):
        assert isinstance(boardname, str)
        assert isinstance(pinname, str)
        assert socket is None or isinstance(socket, str)
        self.boardname = boardname
        self.socket = socket
        self.pinname = pinname

    def __call__(self):
        return (self.boardname, self.socket, self.pinname)

    def __hash__(self):
        return hash(self())

    def __eq__(self, rhs):
        return rhs == self()
