

def Enum(*sequential, **named):
    """This is a hack and not does not enforce normal enumeration behaivor. 
    
    So use it in friendly ways.  Either expicilty assign unique values or dont assign at all.
    Explicit enumeration also allows any value to be assigned. numbers, strings, whateva
    
    Also, I'm capitalizing this method name so it appears as a constructor call.  maybe this is cursed naming...


    usage:  for auto-enumeration:      Name = enum('ALICE', 'BOB', 'CAROL')
            for explicit enumeration:  Name = enum(ALICE=0, BOB=42, CAROL=314)
            
    Note the parameters as strings for auto-enumeration
    
    
    Avoid errors:
    You could get duplicate enum values by calling:
    
        Name = enum('ALICE', 'BOB', CAROL=0)
    
    in above case:
        Name.BOB   == 0
        Name.CAROL == 1
        Name.DAVE  == 0     O_o
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    
    # TODO: could add a check here for duplicate values 
    
    # type() with three arguments returns a new type class or essentially a metaclass
    # E.g.:
    # 'Enum'  is this type of object returned
    # ()      is tuple of base classes, so no base classes
    # enums   dict that holds namespaces for class: i.e.: your arg, kwargs
    #
    return type('Enum', (), enums)