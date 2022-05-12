import React, {useEffect} from 'react';
import PropTypes from 'prop-types';
import { useTheme, styled } from '@mui/material/styles';
import { VariableSizeList } from 'react-window';
import useMediaQuery from '@mui/material/useMediaQuery';
import Autocomplete, { autocompleteClasses } from '@mui/material/Autocomplete';
import Popper from '@mui/material/Popper';
import ListSubheader from '@mui/material/ListSubheader';
import Typography from '@mui/material/Typography';




import {
    Box, CircularProgress,
    FormControl,
    FormControlLabel,
    InputLabel,
    MenuItem,
    Select, Switch,
    TextField
} from "@mui/material";


const LISTBOX_PADDING = 8; // px

function renderRow(props) {
    const { data, index, style } = props;
    const dataSet = data[index];
    const inlineStyle = {
        ...style,
        top: style.top + LISTBOX_PADDING,
    };

    if (dataSet.hasOwnProperty('group')) {
        return (
            <ListSubheader key={dataSet.key} component="div" style={inlineStyle}>
                {dataSet.group}
            </ListSubheader>
        );
    }

    return (
        <Typography component="li" {...dataSet[0]} noWrap style={inlineStyle}>
            {dataSet[1]}
        </Typography>
    );
}

const OuterElementContext = React.createContext({});

const OuterElementType = React.forwardRef((props, ref) => {
    const outerProps = React.useContext(OuterElementContext);
    return <div ref={ref} {...props} {...outerProps} />;
});

function useResetCache(data) {
    const ref = React.useRef(null);
    React.useEffect(() => {
        if (ref.current != null) {
            ref.current.resetAfterIndex(0, true);
        }
    }, [data]);
    return ref;
}

const StyledPopper = styled(Popper)({
    [`& .${autocompleteClasses.listbox}`]: {
        boxSizing: 'border-box',
        '& ul': {
            padding: 0,
            margin: 0,
        },
    },
});
// Adapter for react-window
const ListboxComponent = React.forwardRef(function ListboxComponent(props, ref) {
    const { children, ...other } = props;
    const itemData = [];
    children.forEach((item) => {
        itemData.push(item);
        itemData.push(...(item.children || []));
    });

    const theme = useTheme();
    const smUp = useMediaQuery(theme.breakpoints.up('sm'), {
        noSsr: true,
    });

    const itemCount = itemData.length;
    const itemSize = smUp ? 36 : 48;

    const getChildSize = (child) => {
        if (child.hasOwnProperty('group')) {
            return 48;
        }

        return itemSize;
    };

    const getHeight = () => {
        if (itemCount > 8) {
            return 8 * itemSize;
        }
        return itemData.map(getChildSize).reduce((a, b) => a + b, 0);
    };

    const gridRef = useResetCache(itemCount);

    return (
        <div ref={ref}>
            <OuterElementContext.Provider value={other}>
                <VariableSizeList
                    itemData={itemData}
                    height={getHeight() + 2 * LISTBOX_PADDING}
                    width="100%"
                    ref={gridRef}
                    outerElementType={OuterElementType}
                    innerElementType="ul"
                    itemSize={(index) => getChildSize(itemData[index])}
                    overscanCount={5}
                    itemCount={itemCount}
                >
                    {renderRow}
                </VariableSizeList>
            </OuterElementContext.Provider>
        </div>
    );
});

ListboxComponent.propTypes = {
    children: PropTypes.node,
};


const Search = ({modelType, setModelType, recommenderType, setRecommenderType, searchByUser, validUsers, validMovies, setUserOrMovieName, setSearchByUser}) => {

    return (
        <Box sx={{
            color: 'text.primary',
            display: 'flex',
            justifyContent: 'center',
            width: '100%',
        }}>
            <Box sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '10rem',
                width: "70%",
                border: '0.01rem solid',
                borderColor: 'text.divider',
                paddingX: '7rem',
                paddingY: '1rem'
            }}>
                <FormControl sx={{ m: 1, minWidth: 120 }}>
                    <InputLabel id="recommender-type-label">Recommender Type</InputLabel>
                    <Select
                        labelId="recommender-type-label"
                        id="demo-simple-select-helper"
                        value={recommenderType}
                        label="Recommender Type"
                        onChange={(e)=>setRecommenderType(e.target.value)}
                    >
                        <MenuItem value={"collaborative"}>Collaborative Filtering</MenuItem>
                        <MenuItem value={"contentbased"}>Content Based Filtering</MenuItem>
                    </Select>
                    {/*<FormHelperText>Model Type</FormHelperText>*/}
                </FormControl>
                {recommenderType === "collaborative" ?(
                    <FormControl sx={{ m: 1, minWidth: 120 }}>
                        <InputLabel id="model-type-label" >Model Type</InputLabel>
                        <Select
                            labelId="model-type-label"
                            id="demo-simple-select-helper"
                            value={modelType}
                            label="Model Type"
                            onChange={(e)=>setModelType(e.target.value)}
                        >
                            <MenuItem value={"KNN"}>KNN</MenuItem>
                            <MenuItem value={"item"}>Item to Item Similarity</MenuItem>
                        </Select>
                    </FormControl>
                    )
                :
                    <FormControl sx={{ m: 1, minWidth: 120 }}>
                        <InputLabel id="model-type-label" >Model Type</InputLabel>
                        <Select
                            labelId="model-type-label"
                            id="demo-simple-select-helper"
                            value={modelType}
                            label="Model Type"
                            disabled
                        >
                            <MenuItem value={modelType}>{modelType}</MenuItem>
                        </Select>
                    </FormControl>
                }
                {validMovies !== null && !searchByUser  && (
                    <FormControl sx={{ m: 1, minWidth: validMovies.length === 0 ? 0 : 120 }}>
                        {validMovies.length === 0 ? (
                            <CircularProgress size={20} sx={{marginLeft: "2rem"}} />
                        ): (
                            <Autocomplete
                                id="combo-box-demo"
                                options={validMovies}

                                onChange={(event, newValue) => {
                                    setUserOrMovieName(newValue);
                                }}
                                sx={{ width: 300 }}
                                disableListWrap
                                PopperComponent={StyledPopper}
                                ListboxComponent={ListboxComponent}
                                groupBy={(option) => option[0].toUpperCase()}
                                renderOption={(props, option) => [props, option]}
                                renderGroup={(params) => params}
                                renderInput={(params) => <TextField {...params} label={searchByUser ? 'User Id' : 'Movie Name'} />}
                            />
                        )}
                    </FormControl>
                )}
                {validUsers !== null && searchByUser  && (
                    <FormControl sx={{ m: 1, minWidth: 120 }}>
                        {validUsers.length === 0 ? (
                            <CircularProgress />
                        ): (
                            <Autocomplete
                                id="combo-box-deo"
                                options={validUsers}
                                onChange={(event, newValue) => {
                                    setUserOrMovieName(newValue);
                                }}
                                sx={{ width: 300 }}
                                disableListWrap
                                PopperComponent={StyledPopper}
                                ListboxComponent={ListboxComponent}
                                getOptionLabel={(option) => option.toString()}
                                renderOption={(props, option) => [props, option]}
                                renderGroup={(params) => params}
                                renderInput={(params) => <TextField {...params} label={searchByUser ? 'User Id' : 'Movie Name'} />}
                            />
                        )}
                    </FormControl>
                )}
                {recommenderType === "collaborative" && (
                    <FormControlLabel
                        control={
                            <Switch
                                checked={searchByUser}
                                onChange={(e)=>setSearchByUser(e.target.checked)}
                                inputProps={{ 'aria-label': 'controlled' }}
                            />
                        }
                        label="Search by user Id"
                        sx={{
                            ml: "2rem"
                        }}
                    />
                )}
            </Box>
        </Box>
    );
};

export default Search;
