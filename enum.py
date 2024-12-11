import collections

def Enum(*sequential, **named):
    """This is a hack and not does not enforce normal enumeration behaviour.
    
    So use it in friendly ways.  Either explicitly assign unique values or don't assign at all.
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

    TODO: this qualifies for unit-testing.  add unit-testing .
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)

    # check for duplicate values.  Duplicate values are invalid enumerations
    key_count = len(list(enums.keys()))
    unique_value_count = len(set(enums.values()))
    if key_count != unique_value_count:
        raise ValueError('Enumerations need to have unique values.')

    # CircuitPython collections modules does not (yet?) have Counter class
    # enum_value_counts = Counter(enums.values())  # dictionary: keys are enum values, values are counts of occurrences
    # duplicates = {k:v for k,v in enums.items() if enum_value_counts[v] > 1}
    # if duplicates:
    #     raise ValueError(f'Enumerations need to have unique values. Duplicates are :{duplicates}')

    # type() with three arguments returns a new type class or essentially a metaclass
    # E.g.:
    # 'Enum'  is this type of object returned
    # ()      is tuple of base classes, so no base classes
    # enums   dict that holds namespaces for class: i.e.: your arg, kwargs
    #
    return type('Enum', (), enums)