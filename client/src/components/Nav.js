import {Box, Link, Typography} from "@mui/material";
import { ReactComponent as GithubIcon } from '../assets/github-icon.svg';


export const Nav = () => {
    return (
        <Box sx={{display: "flex", width: "80%",  paddingX: "5rem", paddingY: "2rem",  justifyContent: "space-between"}}>
            <Typography variant="h5" component="div" color='primary'>
                Recommender System
            </Typography>
            <Link  href="https://github.com/praise2112/TP6-Recommneder_System"
               target="_blank"
               title="Github Page"
               rel="noopener noreferrer"
               className="github-link"
            >
                <GithubIcon />
                Github
            </Link >
        </Box>
    )
}
